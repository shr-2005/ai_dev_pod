"""
Setup script - initializes ChromaDB with templates and validates configuration.
Run once before starting the app: python setup.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def main():
    print("=" * 60)
    print("  AI Virtual Development Pod — Setup")
    print("=" * 60)

    # Step 1: Check .env file
    print("\n[1/5] Checking configuration...")
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("  ✅ Created .env from .env.example")
        print("  ⚠️  Edit .env and set GROQ_API_KEY before running the app!")
    elif env_file.exists():
        print("  ✅ .env file found")
    else:
        print("  ⚠️  No .env file found. Create one based on .env.example")

    from dotenv import load_dotenv
    load_dotenv()

    # Validate keys
    groq_key = os.getenv("GROQ_API_KEY", "")
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

    if not groq_key or groq_key == "your_groq_api_key_here":
        print("  ❌ GROQ_API_KEY not set.")
        print("     Get your free key at: https://console.groq.com")
    else:
        print(f"  ✅ GROQ_API_KEY found ({groq_key[:8]}...)")

    if not hf_token or hf_token == "your_huggingface_token_here":
        print("  ⚠️  HUGGINGFACEHUB_API_TOKEN not set (needed for embeddings).")
        print("     Get it at: https://huggingface.co/settings/tokens")
    else:
        print(f"  ✅ HUGGINGFACEHUB_API_TOKEN found ({hf_token[:8]}...)")

    # Step 2: Create directories
    print("\n[2/5] Creating directories...")
    dirs = [
        "artifacts/user_stories",
        "artifacts/design_docs",
        "artifacts/code",
        "artifacts/test_reports",
        "chroma_db",
        "templates",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("  ✅ All directories created")

    # Step 3: Check groq package
    print("\n[3/5] Checking Groq package...")
    try:
        import groq
        print(f"  ✅ groq package found (v{groq.__version__})")
    except ImportError:
        print("  ❌ groq package not installed.")
        print("     Run: pip install groq")

    # Step 4: Load templates into ChromaDB
    print("\n[4/5] Loading templates into ChromaDB...")
    try:
        from core.vector_store import get_vector_store
        vs = get_vector_store()
        vs.load_templates_from_disk("./templates")

        template_types = ["user_stories", "design_doc", "test_cases"]
        loaded = 0
        for tt in template_types:
            template = vs.get_template(tt)
            if template:
                loaded += 1
                print(f"  ✅ Template loaded: {tt}")
            else:
                print(f"  ⚠️  Template not found: {tt}")
        print(f"  Loaded {loaded}/{len(template_types)} templates")
    except Exception as e:
        print(f"  ❌ Error loading templates: {e}")
        print("     Templates will be skipped during generation (not critical)")

    # Step 5: Verify embedding model
    print("\n[5/5] Verifying embedding model...")
    try:
        from core.vector_store import get_vector_store
        vs = get_vector_store()
        test_embedding = vs.embed(["test sentence"])
        if test_embedding and len(test_embedding[0]) > 0:
            print(f"  ✅ MiniLM embedding model ready ({len(test_embedding[0])} dimensions)")
        else:
            print("  ⚠️  Embedding model returned empty result")
    except Exception as e:
        print(f"  ❌ Error loading embedding model: {e}")
        print("     Run: pip install sentence-transformers")

    # Summary
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print()
    print("  To start the application:")
    print("    streamlit run app.py")
    print()
    if not groq_key or groq_key == "your_groq_api_key_here":
        print("  ⚠️  Remember to set GROQ_API_KEY in your .env file!")
        print("     https://console.groq.com → API Keys → Create Key")
    print()


if __name__ == "__main__":
    main()