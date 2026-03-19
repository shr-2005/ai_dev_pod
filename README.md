# 🤖 AI Virtual Development Pod

An intelligent multi-agent system that simulates a complete software development team — from requirements analysis to code generation and automated testing.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                           │
│  Dashboard | Pipeline | Artifacts | Test Runner | PM Chat       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                 ┌─────────▼─────────┐
                 │  Project Lead     │
                 │  Orchestrator     │  ← CrewAI
                 └─────────┬─────────┘
          ┌────────┬────────┼────────┬────────┐
          ▼        ▼        ▼        ▼        ▼
     ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
     │  BA  │ │Design│ │ Dev  │ │ Test │ │  QA  │
     │Agent │ │Agent │ │Agent │ │Agent │ │Agent │
     └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
          │        │        │        │
          └────────┴────────┴────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                                 ▼
   ┌─────────────┐                 ┌────────────────┐
   │   Llama 3   │                 │   ChromaDB     │
   │  8B Instruct│                 │  + MiniLM      │
   │  HuggingFace│                 │  Embeddings    │
   └─────────────┘                 └────────────────┘
```

## 🤝 Agent Roles

| Agent | Role | Output |
|-------|------|--------|
| **Business Analyst** | Transforms requirements into user stories | User stories with acceptance criteria |
| **Design Agent** | Creates software architecture | Design document with schema, APIs |
| **Developer Agent** | Generates production code | Complete, documented source code |
| **Testing Agent** | Creates and runs tests | Test cases + execution report |

## 🛠️ Technology Stack

- **LLM:** Meta Llama 3 8B Instruct (via Hugging Face Router)
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector DB:** ChromaDB (local persistent)
- **Orchestration:** CrewAI
- **Frontend:** Streamlit
- **Language:** Python 3.10+

---

## 🚀 Quick Start

### 1. Clone / Download the Project

```bash
# If using Git
git clone <your-repo-url>
cd ai_dev_pod

# Or just navigate to the folder in VS Code
```

### 2. Create a Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example env file
cp .env.example .env
```

Edit `.env` and set your Hugging Face token:
```
HF_TOKEN=hf_your_actual_token_here
```

Get your free token at: https://huggingface.co/settings/tokens

> **Note:** You need access to `meta-llama/Meta-Llama-3-8B-Instruct`. Request access at: https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct

### 5. Run Setup Script

```bash
python setup.py
```

This will:
- Validate your configuration
- Create required directories
- Load templates into ChromaDB
- Verify the embedding model

### 6. Launch the Application

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## 📖 Usage Guide

### Running the Full Pipeline

1. Navigate to **🚀 Run Pipeline** in the sidebar
2. Enter your **Project Name** (e.g., "Online Banking System")
3. Enter **Business Requirements** (or load a sample)
4. Select **Language** and **Framework**
5. Click **🚀 Launch Pipeline**

The pipeline runs 4 phases sequentially:
1. **BA Agent** → User Stories
2. **Design Agent** → Design Document
3. **Developer Agent** → Source Code
4. **Testing Agent** → Test Cases + Execution

### Viewing Artifacts

Each artifact type has its own page:
- **📋 User Stories** — View and download user stories
- **🏗️ Design Doc** — Architecture and design document
- **💻 Code** — Generated source code
- **🧪 Test Cases** — Test suite and execution results

### PM Chat

Go to **💬 PM Chat** to have a conversation with the AI Project Lead:
- Ask about project status
- Request quality assessments
- Query specific artifacts
- Get explanations of design decisions

---

## 📁 Project Structure

```
ai_dev_pod/
├── app.py                    # Main Streamlit entry point
├── setup.py                  # Setup and initialization script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
│
├── core/                     # Core infrastructure
│   ├── llm_client.py         # Llama 3 8B via HuggingFace
│   ├── vector_store.py       # ChromaDB + MiniLM embeddings
│   ├── artifact_manager.py   # Artifact persistence
│   └── orchestrator.py       # CrewAI pipeline orchestration
│
├── agents/                   # AI Agent implementations
│   ├── ba_agent.py           # Business Analyst Agent
│   ├── design_agent.py       # Design Agent
│   ├── dev_agent.py          # Developer Agent
│   └── test_agent.py         # Testing Agent
│
├── pages/                    # Streamlit pages
│   ├── dashboard.py          # Main dashboard
│   ├── pipeline_runner.py    # Pipeline execution
│   ├── artifact_viewer.py    # Generic artifact viewer
│   ├── test_runner.py        # Test execution UI
│   └── pm_chat.py            # PM chat interface
│
├── templates/                # Artifact templates (loaded into ChromaDB)
│   ├── user_stories.txt      # User story template
│   ├── design_doc.txt        # Design document template
│   └── test_cases.txt        # Test cases template
│
├── artifacts/                # Generated artifacts (auto-created)
│   ├── user_stories/
│   ├── design_docs/
│   ├── code/
│   └── test_reports/
│
├── chroma_db/                # ChromaDB persistence (auto-created)
└── utils/
    └── helpers.py            # Utility functions
```

---

## ⚙️ Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN` | — | **Required.** Hugging Face API token |
| `LLM_MODEL` | `meta-llama/Meta-Llama-3-8B-Instruct` | LLM model to use |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage location |
| `ARTIFACTS_DIR` | `./artifacts` | Artifacts storage location |
| `MAX_TOKENS` | `2048` | Max tokens per generation |
| `TEMPERATURE` | `0.7` | LLM temperature (0-1) |

---

## 🔧 Troubleshooting

**"Model is loading" error**
→ The Llama 3 model takes ~30s to warm up on HuggingFace. Wait and retry.

**"HF_TOKEN not set"**
→ Make sure `.env` file exists with your token. Run `python setup.py` to verify.

**"Access denied" for Llama 3**
→ Request model access at https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct

**ChromaDB errors**
→ Delete `chroma_db/` directory and re-run `python setup.py`

**Streamlit import errors**
→ Ensure virtual environment is activated and `pip install -r requirements.txt` completed

---

## 📋 Requirements

- Python 3.10+
- 4GB+ RAM (for embedding model)
- Internet connection (for HuggingFace API calls)
- Hugging Face account with Llama 3 access

---

## 🎯 Features

- ✅ Full SDLC simulation with 4 specialized AI agents
- ✅ Meta Llama 3 8B via HuggingFace Router
- ✅ Semantic template retrieval with ChromaDB + MiniLM
- ✅ Automated test execution with pytest
- ✅ Conversational PM chat interface
- ✅ Artifact download and persistence
- ✅ Sample projects for quick demo
- ✅ Real-time pipeline progress
- ✅ Individual phase execution support

---

*Built with ❤️ using Streamlit, CrewAI, LangChain, ChromaDB, and Meta Llama 3*
