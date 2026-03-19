"""
Dashboard Page - Project overview and agent status.
"""
import streamlit as st
from datetime import datetime


def render_dashboard():
    """Render the main dashboard."""
    st.markdown("""
    <div class='main-header'>
        <h1>🤖 AI Virtual Development Pod</h1>
        <p>Intelligent multi-agent system for end-to-end software development lifecycle</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    results = st.session_state.get("pipeline_results", {})
    project_name = st.session_state.get("project_name", "—")

    col1, col2, col3, col4, col5 = st.columns(5)

    artifacts_count = sum([
        1 for k in ["user_stories", "design_doc", "code", "test_cases"]
        if k in results and results[k]
    ])

    test_results = results.get("test_results", {})
    passed = test_results.get("passed", 0) if isinstance(test_results, dict) else 0
    failed = test_results.get("failed", 0) if isinstance(test_results, dict) else 0
    total_tests = passed + failed
    pass_rate = f"{(passed/total_tests*100):.0f}%" if total_tests > 0 else "—"

    with col1:
        st.metric("Project", project_name[:12] + "..." if len(project_name) > 12 else project_name or "None")
    with col2:
        st.metric("Artifacts Generated", artifacts_count)
    with col3:
        st.metric("Tests Passed", passed if total_tests > 0 else "—")
    with col4:
        st.metric("Tests Failed", failed if total_tests > 0 else "—")
    with col5:
        st.metric("Pass Rate", pass_rate)

    st.markdown("---")

    # Agent cards
    st.markdown("### 🤝 Development Team Agents")

    agents = [
        {
            "icon": "📋",
            "name": "Business Analyst Agent",
            "role": "Requirements Analysis",
            "description": "Transforms high-level business requirements into structured Agile user stories with acceptance criteria, priorities, and story point estimates.",
            "phase": "user_stories",
            "color": "#6366f1",
        },
        {
            "icon": "🏗️",
            "name": "Design Agent",
            "role": "Software Architecture",
            "description": "Creates comprehensive software design documents including system architecture, database schema, API contracts, and technology stack decisions.",
            "phase": "design_doc",
            "color": "#3b82f6",
        },
        {
            "icon": "💻",
            "name": "Developer Agent",
            "role": "Code Generation",
            "description": "Generates production-ready, well-documented code based on user stories and design documents. Supports multiple languages and frameworks.",
            "phase": "code",
            "color": "#f59e0b",
        },
        {
            "icon": "🧪",
            "name": "Testing Agent",
            "role": "QA & Test Execution",
            "description": "Creates comprehensive test suites (unit, integration, e2e) and executes automated tests against generated code, producing detailed reports.",
            "phase": "test_cases",
            "color": "#22c55e",
        },
    ]

    cols = st.columns(2)
    for i, agent in enumerate(agents):
        with cols[i % 2]:
            phase_done = agent["phase"] in results and results[agent["phase"]]
            status_html = (
                '<span class="status-badge status-done">✓ Done</span>'
                if phase_done
                else '<span class="status-badge status-ready">Ready</span>'
            )
            st.markdown(f"""
            <div class="agent-card" style="border-top: 3px solid {agent['color']};">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                    <div>
                        <h4 style="margin:0;">{agent['icon']} {agent['name']}</h4>
                        <p style="color:{agent['color']}; font-size:0.8rem; margin:0.2rem 0 0;">{agent['role']}</p>
                    </div>
                    {status_html}
                </div>
                <p>{agent['description']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Pipeline overview
    st.markdown("### 🔄 SDLC Pipeline")

    pipeline_steps = [
        ("📋", "Business Analysis", "Generate user stories from requirements", "user_stories"),
        ("🏗️", "System Design", "Create architecture and design documents", "design_doc"),
        ("💻", "Development", "Generate production-ready code", "code"),
        ("🧪", "Testing", "Create and execute automated test suites", "test_cases"),
    ]

    for step_icon, step_name, step_desc, phase in pipeline_steps:
        done = phase in results and results[phase]
        status_color = "#22c55e" if done else "#374151"
        status_text = "Completed" if done else "Pending"
        status_icon = "✅" if done else "⭕"

        st.markdown(f"""
        <div class="pipeline-step">
            <div class="step-icon">{step_icon}</div>
            <div class="step-info" style="flex:1;">
                <h5>{step_name}</h5>
                <p>{step_desc}</p>
            </div>
            <div>
                <span style="color:{status_color}; font-size:0.85rem;">{status_icon} {status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick start
    if not results:
        st.info("👉 **Get started:** Go to **🚀 Run Pipeline** to begin your first project, or click below.")
        if st.button("🚀 Start New Project", type="primary", use_container_width=False):
            st.session_state.current_page = "pipeline"
            st.rerun()
    else:
        st.success(f"✅ Pipeline completed for **{project_name}**. Explore the artifacts using the sidebar navigation.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Chat with Project Lead", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        with col2:
            if st.button("🚀 Run New Pipeline", use_container_width=True):
                st.session_state.current_page = "pipeline"
                st.rerun()

    # Tech stack info
    with st.expander("🛠️ Technology Stack"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **AI/ML**
            - Meta Llama 3 8B Instruct
            - HuggingFace Router
            - MiniLM-L6-v2 embeddings
            - CrewAI orchestration
            """)
        with col2:
            st.markdown("""
            **Storage & Retrieval**
            - ChromaDB vector database
            - Semantic template retrieval
            - Artifact persistence
            - Session state management
            """)
        with col3:
            st.markdown("""
            **Frontend**
            - Streamlit
            - Custom CSS theming
            - Interactive UI components
            - Real-time progress tracking
            """)
