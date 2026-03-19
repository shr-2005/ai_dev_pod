"""
AI Virtual Development Pod - Main Streamlit Application
"""
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration - MUST be first Streamlit call
st.set_page_config(
    page_title="AI Dev Pod",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .main-header h1 {
        color: #e2e8f0;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: #94a3b8;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    .agent-card {
        background: #1e293b;
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        transition: border-color 0.2s;
    }
    
    .agent-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    .agent-card h4 {
        color: #e2e8f0;
        margin: 0 0 0.5rem 0;
    }
    
    .agent-card p {
        color: #94a3b8;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-ready {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .status-running {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    
    .status-done {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .metric-card {
        background: #1e293b;
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #818cf8;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
    }
    
    /* Chat bubbles */
    .chat-user {
        background: #1e3a5f;
        border-left: 3px solid #3b82f6;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    
    .chat-assistant {
        background: #1e2d3d;
        border-left: 3px solid #6366f1;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    
    /* Artifact viewer */
    .artifact-content {
        background: #0f172a;
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        padding: 1.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Pipeline steps */
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.8rem 1rem;
        background: #1e293b;
        border-radius: 8px;
        margin: 0.4rem 0;
    }
    
    .step-icon {
        font-size: 1.5rem;
        width: 2rem;
        text-align: center;
    }
    
    .step-info h5 { margin: 0; color: #e2e8f0; }
    .step-info p { margin: 0; color: #64748b; font-size: 0.85rem; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide the multipage nav dropdown Streamlit auto-generates */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Sidebar nav */
    .sidebar-nav-item {
        padding: 0.6rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        color: #94a3b8;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%);
        border: none;
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown("""
        <div style='padding: 1rem 0.5rem 1.5rem;'>
            <h2 style='color: #e2e8f0; margin: 0; font-size: 1.2rem;'>🤖 AI Dev Pod</h2>
            <p style='color: #64748b; font-size: 0.8rem; margin: 0.3rem 0 0;'>Virtual Development Team</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        pages = {
            "🏠 Dashboard": "dashboard",
            "🚀 Run Pipeline": "pipeline",
            "📋 User Stories": "user_stories",
            "🏗️ Design Doc": "design",
            "💻 Code": "code",
            "🧪 Test Cases": "tests",
            "💬 PM Chat": "chat",
        }

        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        for label, page_key in pages.items():
            is_active = st.session_state.current_page == page_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # Quick status
        st.markdown("<p style='color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Pipeline Status</p>", unsafe_allow_html=True)

        if "pipeline_results" in st.session_state and st.session_state.pipeline_results:
            results = st.session_state.pipeline_results
            phases = ["user_stories", "design_doc", "code", "test_cases"]
            icons = ["📋", "🏗️", "💻", "🧪"]
            labels = ["User Stories", "Design", "Code", "Tests"]
            for phase, icon, label in zip(phases, icons, labels):
                has = phase in results and results[phase]
                color = "#22c55e" if has else "#374151"
                st.markdown(f"<div style='display:flex;align-items:center;gap:0.5rem;padding:0.2rem 0;'><span>{icon}</span><span style='color:{color};font-size:0.85rem;'>{label}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #374151; font-size: 0.85rem;'>No pipeline run yet</p>", unsafe_allow_html=True)

        # Groq API status
        st.markdown("---")
        groq_key = os.getenv("GROQ_API_KEY", "")
        if groq_key and groq_key != "your_groq_api_key_here":
            st.markdown("🟢 <span style='color:#22c55e;font-size:0.8rem;'>Groq API Connected</span>", unsafe_allow_html=True)
        else:
            st.markdown("🔴 <span style='color:#ef4444;font-size:0.8rem;'>Set GROQ_API_KEY in .env</span>", unsafe_allow_html=True)


def main():
    """Main application router."""
    # Initialize session state
    if "pipeline_results" not in st.session_state:
        st.session_state.pipeline_results = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "project_name" not in st.session_state:
        st.session_state.project_name = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    render_sidebar()

    # Route to page — imports from _pages (renamed from pages to avoid
    # Streamlit's built-in multipage nav auto-detection)
    page = st.session_state.current_page

    if page == "dashboard":
        from _pages.dashboard import render_dashboard
        render_dashboard()
    elif page == "pipeline":
        from _pages.pipeline_runner import render_pipeline
        render_pipeline()
    elif page == "user_stories":
        from _pages.artifact_viewer import render_artifact_viewer
        render_artifact_viewer("user_stories", "📋 User Stories")
    elif page == "design":
        from _pages.artifact_viewer import render_artifact_viewer
        render_artifact_viewer("design_doc", "🏗️ Design Document")
    elif page == "code":
        from _pages.artifact_viewer import render_artifact_viewer
        render_artifact_viewer("code", "💻 Generated Code")
    elif page == "tests":
        from _pages.test_runner import render_test_runner
        render_test_runner()
    elif page == "chat":
        from _pages.pm_chat import render_pm_chat
        render_pm_chat()


if __name__ == "__main__":
    main()