"""
Vector Store - ChromaDB with MiniLM embeddings for template retrieval.
Uses modern PersistentClient API (chromadb >= 0.5.0).
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    """ChromaDB-based vector store with MiniLM embeddings."""

    def __init__(self):
        self.persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Ensure persist directory exists
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        # Modern PersistentClient API (chromadb >= 0.5.0)
        self.client = chromadb.PersistentClient(path=self.persist_dir)

        self._embedding_model = None
        self._templates_collection = None
        self._artifacts_collection = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(self.embedding_model_name)
        return self._embedding_model

    @property
    def templates_collection(self):
        if self._templates_collection is None:
            self._templates_collection = self.client.get_or_create_collection(
                name="templates",
                metadata={"hnsw:space": "cosine"},
            )
        return self._templates_collection

    @property
    def artifacts_collection(self):
        if self._artifacts_collection is None:
            self._artifacts_collection = self.client.get_or_create_collection(
                name="artifacts",
                metadata={"hnsw:space": "cosine"},
            )
        return self._artifacts_collection

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.embedding_model.encode(texts, convert_to_numpy=True).tolist()

    def add_template(self, template_id: str, template_type: str, content: str, metadata: Dict = None):
        embedding = self.embed([content])[0]
        meta = {"type": template_type, "template_id": template_id}
        if metadata:
            meta.update(metadata)
        self.templates_collection.upsert(
            ids=[template_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta],
        )

    def get_template(self, template_type: str, query: str = None, n_results: int = 1) -> Optional[str]:
        if query is None:
            query = template_type
        embedding = self.embed([query])[0]
        try:
            results = self.templates_collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where={"type": template_type},
            )
            if results and results["documents"] and results["documents"][0]:
                return results["documents"][0][0]
        except Exception:
            pass
        return None

    def add_artifact(self, artifact_id: str, artifact_type: str, content: str, metadata: Dict = None):
        embedding = self.embed([content[:500]])[0]
        meta = {"type": artifact_type, "artifact_id": artifact_id}
        if metadata:
            meta.update(metadata)
        self.artifacts_collection.upsert(
            ids=[artifact_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta],
        )

    def search_artifacts(self, query: str, artifact_type: str = None, n_results: int = 3) -> List[Dict]:
        embedding = self.embed([query])[0]
        where_filter = {"type": artifact_type} if artifact_type else None
        try:
            results = self.artifacts_collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where_filter,
            )
            items = []
            if results and results["documents"] and results["documents"][0]:
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ):
                    items.append({"content": doc, "metadata": meta, "distance": dist})
            return items
        except Exception:
            return []

    def load_templates_from_disk(self, templates_dir: str):
        templates_path = Path(templates_dir)
        if not templates_path.exists():
            return
        for template_file in templates_path.glob("*.txt"):
            template_type = template_file.stem
            content = template_file.read_text(encoding="utf-8")
            self.add_template(
                template_id=f"template_{template_type}",
                template_type=template_type,
                content=content,
                metadata={"filename": template_file.name},
            )


_vector_store: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store