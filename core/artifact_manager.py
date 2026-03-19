"""
Artifact Manager - Handles all generated project artifacts.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class ArtifactManager:
    """Manages all generated project artifacts."""

    ARTIFACT_TYPES = {
        "user_stories": "user_stories",
        "design_doc": "design_docs",
        "code": "code",
        "test_cases": "test_reports",
        "test_report": "test_reports",
    }

    def __init__(self):
        self.base_dir = Path(os.getenv("ARTIFACTS_DIR", "./artifacts"))
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure all artifact directories exist."""
        for sub_dir in self.ARTIFACT_TYPES.values():
            (self.base_dir / sub_dir).mkdir(parents=True, exist_ok=True)

    def save(
        self,
        artifact_type: str,
        content: str,
        project_name: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """Save an artifact to disk and return its path."""
        sub_dir = self.ARTIFACT_TYPES.get(artifact_type, artifact_type)
        artifact_dir = self.base_dir / sub_dir

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() else "_" for c in project_name)
            filename = f"{safe_name}_{artifact_type}_{timestamp}.md"

        filepath = artifact_dir / filename

        # Build content with metadata header
        full_content = self._build_content(content, metadata or {}, project_name, artifact_type)
        filepath.write_text(full_content, encoding="utf-8")

        return str(filepath)

    def _build_content(self, content: str, metadata: Dict, project_name: str, artifact_type: str) -> str:
        """Add metadata header to artifact content."""
        header = f"""---
project: {project_name}
artifact_type: {artifact_type}
generated_at: {datetime.now().isoformat()}
"""
        for k, v in metadata.items():
            header += f"{k}: {v}\n"
        header += "---\n\n"
        return header + content

    def load(self, artifact_type: str, filename: str) -> Optional[str]:
        """Load an artifact from disk."""
        sub_dir = self.ARTIFACT_TYPES.get(artifact_type, artifact_type)
        filepath = self.base_dir / sub_dir / filename
        if filepath.exists():
            return filepath.read_text(encoding="utf-8")
        return None

    def list_artifacts(self, artifact_type: Optional[str] = None) -> List[Dict]:
        """List all available artifacts, optionally filtered by type."""
        artifacts = []
        if artifact_type:
            dirs_to_scan = [(artifact_type, self.ARTIFACT_TYPES.get(artifact_type, artifact_type))]
        else:
            dirs_to_scan = list(self.ARTIFACT_TYPES.items())

        seen_dirs = set()
        for art_type, sub_dir in dirs_to_scan:
            if sub_dir in seen_dirs:
                continue
            seen_dirs.add(sub_dir)
            artifact_dir = self.base_dir / sub_dir
            if artifact_dir.exists():
                for f in sorted(artifact_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
                    stat = f.stat()
                    artifacts.append({
                        "type": art_type,
                        "filename": f.name,
                        "path": str(f),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    })
        return artifacts

    def get_latest(self, artifact_type: str) -> Optional[Dict]:
        """Get the most recently created artifact of a given type."""
        artifacts = self.list_artifacts(artifact_type)
        if artifacts:
            latest = artifacts[0]
            content = self.load(artifact_type, latest["filename"])
            latest["content"] = content
            return latest
        return None

    def get_summary(self) -> Dict:
        """Get a summary count of all artifacts."""
        summary = {}
        seen_dirs = set()
        for art_type, sub_dir in self.ARTIFACT_TYPES.items():
            if sub_dir in seen_dirs:
                continue
            seen_dirs.add(sub_dir)
            artifact_dir = self.base_dir / sub_dir
            count = len(list(artifact_dir.glob("*.md"))) if artifact_dir.exists() else 0
            summary[art_type] = count
        return summary


# Singleton
_artifact_manager: Optional[ArtifactManager] = None


def get_artifact_manager() -> ArtifactManager:
    global _artifact_manager
    if _artifact_manager is None:
        _artifact_manager = ArtifactManager()
    return _artifact_manager
