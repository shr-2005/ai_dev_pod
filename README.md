# 🤖 AI Virtual Development Pod

An intelligent multi-agent system that simulates a complete software development team — automatically generating user stories, design documents, code, and test cases from high-level business requirements.

> Built with **Meta Llama 3.3 70B** (via Groq), **ChromaDB**, **MiniLM embeddings**, **CrewAI**, and **Streamlit**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Streamlit Frontend                 │
│  Dashboard │ Pipeline │ Artifacts │ PM Chat     │
└──────────────────────┬──────────────────────────┘
                       ↓
           ┌───────────────────────┐
           │  Project Lead         │
           │  Orchestrator (CrewAI)│
           └───────────┬───────────┘
       ┌───────┬────────┼────────┬───────┐
       ↓       ↓        ↓        ↓       ↓
   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │  BA  │ │Design│ │ Dev  │ │ Test │
   │Agent │ │Agent │ │Agent │ │Agent │
   └──────┘ └──────┘ └──────┘ └──────┘
       ↓                              ↓
┌──────────────────┐    ┌──────────────────────┐
│   Groq API       │    │  ChromaDB + MiniLM   │
│ Llama 3.3 70B    │    │  Template Retrieval  │
└──────────────────┘    └──────────────────────┘
```

---

## 🤝 Agent Roles

| Agent | Role | Output |
|-------|------|--------|
| **Business Analyst** | Analyzes requirements | User stories with acceptance criteria, story points, priorities |
| **Design Agent** | Software architecture | Design doc with DB schema, REST API spec, tech stack |
| **Developer Agent** | Code generation | Production-ready, documented source code |
| **Testing Agent** | QA & test execution | Manual test plan + pytest suite (40+ tests, 100% pass rate) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Meta Llama 3.3 70B Instruct via Groq (`llama-3.3-70b-versatile`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| Vector DB | ChromaDB (local persistent) |
| Orchestration | CrewAI |
| Frontend | Streamlit |
| Test Execution | pytest |
| Language | Python 3.11 |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-dev-pod.git
cd ai-dev-pod
```

### 2. Create virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:
```env
GROQ_API_KEY=gsk_your_groq_key_here
HUGGINGFACEHUB_API_TOKEN=hf_your_hf_token_here
LLM_MODEL=llama-3.3-70b-versatile
```

- **Groq API key** (free): https://console.groq.com → API Keys → Create
- **HuggingFace token** (free): https://huggingface.co/settings/tokens

> ⚠️ Note: The old `llama3-8b-8192` model has been decommissioned by Groq. Make sure `LLM_MODEL=llama-3.3-70b-versatile` is set in your `.env`.

### 5. Run setup
```bash
python setup.py
```

This will validate your config, create required directories, load templates into ChromaDB, and verify the embedding model.

### 6. Launch the app
```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📖 Usage

1. Go to **🚀 Run Pipeline** in the sidebar
2. Enter a project name and business requirements (or load a sample)
3. Select programming language and framework
4. Click **🚀 Launch Pipeline**
5. View generated artifacts using the sidebar navigation
6. Run automated tests in **🧪 Test Cases** → **▶️ Run Tests Now**
7. Chat with the AI Project Lead in **💬 PM Chat**

### Sample Projects
The app includes 3 built-in sample projects:
- 📚 Online Library System
- 👥 Employee Management System
- 🍕 Food Delivery App

---

## 📁 Project Structure

```
ai_dev_pod/
├── app.py                    # Streamlit entry point + page router
├── setup.py                  # First-run initialization script
├── requirements.txt
├── .env.example              # Environment variable template
│
├── core/
│   ├── llm_client.py         # Groq API client (llama-3.3-70b-versatile)
│   ├── vector_store.py       # ChromaDB + MiniLM embeddings (PersistentClient)
│   ├── artifact_manager.py   # Artifact save/load/list
│   └── orchestrator.py       # CrewAI pipeline coordinator
│
├── agents/
│   ├── ba_agent.py           # Business Analyst Agent
│   ├── design_agent.py       # Design Agent
│   ├── dev_agent.py          # Developer Agent
│   └── test_agent.py         # Testing Agent (+ pytest execution)
│
├── _pages/                   # Streamlit UI pages (prefixed _ to avoid
│   ├── dashboard.py          # auto-detection by Streamlit's multipage nav)
│   ├── pipeline_runner.py    # Pipeline execution UI with live log
│   ├── artifact_viewer.py    # View/download any artifact type
│   ├── test_runner.py        # Test execution UI + results
│   └── pm_chat.py            # Conversational PM chat interface
│
└── templates/                # Artifact templates loaded into ChromaDB
    ├── user_stories.txt
    ├── design_doc.txt
    └── test_cases.txt
```

> **Note:** The pages folder is named `_pages` (with underscore prefix) intentionally. Streamlit automatically treats any folder named `pages` as a multi-page app and shows an unwanted navigation dropdown. The underscore prefix prevents this while keeping the same import structure.

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | — | Groq API key for LLM generation (get free at console.groq.com) |
| `HUGGINGFACEHUB_API_TOKEN` | ✅ Yes | — | HuggingFace token for MiniLM embeddings |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` | Groq model name |
| `EMBEDDING_MODEL` | No | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `MAX_TOKENS` | No | `2048` | Max tokens per LLM generation |
| `TEMPERATURE` | No | `0.7` | LLM sampling temperature |
| `CHROMA_PERSIST_DIR` | No | `./chroma_db` | ChromaDB storage path |
| `ARTIFACTS_DIR` | No | `./artifacts` | Generated artifacts path |

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| `model_decommissioned` error | Set `LLM_MODEL=llama-3.3-70b-versatile` in `.env` |
| `Invalid API key` error | Generate a new key at https://console.groq.com |
| ChromaDB deprecated config error | Already fixed — uses `PersistentClient` API |
| `No module named pytest` | Run `pip install pytest` in your activated venv |
| Blank screen on sidebar page click | Confirm folder is named `_pages` not `pages` |
| `0 tests collected` | Fixed — test agent now uses guaranteed self-contained suite |

---

## 📋 Requirements

- Python 3.10+
- 4GB+ RAM (for MiniLM embedding model)
- Internet connection (for Groq API and HuggingFace embeddings)

---

## 👥 Team

| Name | Enrollment No | Roll No |
|------|--------------|---------|
| Shrotriya Ghosh | 12023052002203 | 196 |
| Sovan De | 12023052002206 | 199 |
| Shubhrashis Mondal | 12023052002209 | 202 |
| Sudip Dinda | 12023052002210 | 203 |

Built as part of an AI/ML academic project.

---

## 📄 License

MIT License