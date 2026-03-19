"""
Pipeline Runner Page - Execute the full AI development pipeline.
"""
import streamlit as st
import threading
import time
from datetime import datetime


def render_pipeline():
    """Render the pipeline runner page."""
    st.markdown("""
    <div class='main-header'>
        <h1>🚀 Run Development Pipeline</h1>
        <p>Configure your project and launch the AI agent pipeline</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize pipeline state
    if "pipeline_log" not in st.session_state:
        st.session_state.pipeline_log = []
    if "pipeline_running" not in st.session_state:
        st.session_state.pipeline_running = False

    # ─── Configuration Form ─────────────────────────────────────────
    st.markdown("### ⚙️ Project Configuration")

    col1, col2 = st.columns([2, 1])

    with col1:
        project_name = st.text_input(
            "Project Name",
            value=st.session_state.get("project_name", ""),
            placeholder="e.g. Online Banking System",
            help="Name of the project to generate artifacts for.",
        )

        business_requirements = st.text_area(
            "Business Requirements",
            height=220,
            placeholder="""Describe your project requirements here. Example:

Build an online library management system that allows:
- Members to register, search and borrow books online
- Librarians to manage book inventory and member accounts
- Automated fine calculation for overdue books
- Email notifications for due dates and availability
- Admin dashboard with reports and analytics""",
            help="Provide high-level business requirements. The BA Agent will transform these into user stories.",
        )

    with col2:
        st.markdown("**Pipeline Options**")

        language = st.selectbox(
            "Programming Language",
            ["Python", "JavaScript", "TypeScript", "Java", "C#"],
            index=0,
        )

        framework = st.selectbox(
            "Framework (optional)",
            ["None", "FastAPI", "Flask", "Django", "Express.js", "React", "Spring Boot"],
            index=0,
        )
        framework = None if framework == "None" else framework

        run_mode = st.radio(
            "Pipeline Mode",
            ["Full Pipeline", "Individual Phases"],
            help="Full Pipeline runs all agents sequentially. Individual lets you run one phase at a time.",
        )

        st.markdown("---")
        st.markdown("**Phase Selection**")
        if run_mode == "Individual Phases":
            run_ba = st.checkbox("📋 Business Analysis", value=True)
            run_design = st.checkbox("🏗️ Design", value=False)
            run_dev = st.checkbox("💻 Development", value=False)
            run_test = st.checkbox("🧪 Testing", value=False)
        else:
            run_ba = run_design = run_dev = run_test = True

    # ─── Sample Requirements ─────────────────────────────────────────
    with st.expander("📚 Load Sample Requirements"):
        samples = {
            "Online Library System": """Build an online library management system that allows:
- Members to register and manage their profiles
- Search and browse book catalog by title, author, genre
- Borrow and return books with due date tracking
- Automatic fine calculation for overdue returns
- Librarians to manage inventory and member accounts
- Admin dashboard with reports on popular books and member activity
- Email notifications for due dates, new arrivals, and overdue reminders""",

            "E-Commerce Platform": """Build a modern e-commerce platform with:
- Product catalog with categories, search and filters
- User registration, login and profile management
- Shopping cart and secure checkout flow
- Payment gateway integration (Stripe)
- Order management and tracking
- Admin panel for product and inventory management
- Review and rating system
- Discount codes and promotional campaigns""",

            "Task Management Tool": """Create a project task management application:
- User authentication with role-based access (Admin, Manager, Developer)
- Create and manage projects and sprints
- Task creation with assignee, due date, priority, and status
- Kanban board view and list view
- Comment threads on tasks
- File attachments on tasks
- Email/in-app notifications for assignments and deadlines
- Dashboard with personal and team productivity metrics""",
        }

        sample_choice = st.selectbox("Choose a sample:", list(samples.keys()))
        if st.button("Load Sample", type="secondary"):
            st.session_state._load_sample = samples[sample_choice]
            st.session_state._load_project = sample_choice
            st.rerun()

    # Load sample if requested
    if hasattr(st.session_state, "_load_sample"):
        business_requirements = st.session_state._load_sample
        project_name = st.session_state._load_project
        del st.session_state._load_sample
        del st.session_state._load_project

    st.markdown("---")

    # ─── Run Button ─────────────────────────────────────────────────
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

    with col_btn1:
        can_run = bool(project_name.strip() and business_requirements.strip())
        run_clicked = st.button(
            "🚀 Launch Pipeline" if run_mode == "Full Pipeline" else "▶️ Run Selected Phases",
            type="primary",
            disabled=not can_run or st.session_state.pipeline_running,
            use_container_width=True,
        )

    with col_btn2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.pipeline_results = {}
            st.session_state.pipeline_log = []
            st.session_state.project_name = ""
            st.rerun()

    if not can_run:
        st.warning("⚠️ Please enter both a project name and business requirements to proceed.")

    # ─── Pipeline Execution ─────────────────────────────────────────
    if run_clicked and can_run:
        st.session_state.project_name = project_name
        st.session_state.pipeline_log = []
        st.session_state.pipeline_results = {}
        _run_pipeline(
            project_name=project_name,
            requirements=business_requirements,
            language=language,
            framework=framework,
            run_ba=run_ba,
            run_design=run_design,
            run_dev=run_dev,
            run_test=run_test,
        )

    # ─── Live Log ─────────────────────────────────────────────────
    if st.session_state.pipeline_log:
        st.markdown("### 📡 Pipeline Log")
        for entry in st.session_state.pipeline_log:
            icon = entry.get("icon", "•")
            msg = entry.get("message", "")
            ts = entry.get("time", "")
            status = entry.get("status", "info")

            color = {"success": "#22c55e", "error": "#ef4444", "running": "#fbbf24", "info": "#94a3b8"}.get(status, "#94a3b8")
            st.markdown(
                f"<div style='padding:0.4rem 0.8rem; background:#1e293b; border-left:3px solid {color}; "
                f"border-radius:0 6px 6px 0; margin:0.3rem 0; font-size:0.9rem; color:#e2e8f0;'>"
                f"<span style='color:{color}'>{icon}</span> {msg} "
                f"<span style='color:#374151; font-size:0.75rem;'>{ts}</span></div>",
                unsafe_allow_html=True,
            )

    # ─── Results Preview ─────────────────────────────────────────
    results = st.session_state.get("pipeline_results", {})
    if results and not st.session_state.pipeline_running:
        st.markdown("---")
        st.markdown("### ✅ Generated Artifacts")

        artifact_map = {
            "user_stories": ("📋", "User Stories"),
            "design_doc": ("🏗️", "Design Document"),
            "code": ("💻", "Generated Code"),
            "test_cases": ("🧪", "Test Cases"),
        }

        cols = st.columns(4)
        for i, (key, (icon, label)) in enumerate(artifact_map.items()):
            with cols[i]:
                if key in results and results[key]:
                    content = results[key]
                    word_count = len(str(content).split())
                    st.success(f"{icon} **{label}**\n\n{word_count} words")
                else:
                    st.info(f"{icon} {label}\n\nNot generated")

        # Navigation hint
        st.markdown("---")
        st.info("📌 Use the **sidebar navigation** to view each artifact in detail, run tests, or chat with the Project Lead.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Chat with Project Lead", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        with col2:
            if st.button("🧪 Go to Test Runner", use_container_width=True):
                st.session_state.current_page = "tests"
                st.rerun()


def _log(message: str, status: str = "info", icon: str = "•"):
    """Add a log entry."""
    st.session_state.pipeline_log.append({
        "message": message,
        "status": status,
        "icon": icon,
        "time": datetime.now().strftime("%H:%M:%S"),
    })


def _run_pipeline(project_name, requirements, language, framework, run_ba, run_design, run_dev, run_test):
    """Execute the pipeline with live progress updates."""
    from core.orchestrator import ProjectLeadOrchestrator

    st.session_state.pipeline_running = True
    orchestrator = ProjectLeadOrchestrator()
    results = {}

    progress_bar = st.progress(0)
    status_text = st.empty()

    phases = []
    if run_ba:
        phases.append("ba")
    if run_design:
        phases.append("design")
    if run_dev:
        phases.append("dev")
    if run_test:
        phases.append("test")

    total_phases = len(phases)
    completed = 0

    try:
        for phase in phases:
            inputs = {
                "requirements": requirements,
                "user_stories": results.get("user_stories", ""),
                "design_doc": results.get("design_doc", ""),
                "code": results.get("code", ""),
                "language": language,
                "framework": framework,
            }

            phase_names = {
                "ba": ("📋", "Business Analysis — generating user stories..."),
                "design": ("🏗️", "Design — creating architecture document..."),
                "dev": ("💻", "Development — generating code..."),
                "test": ("🧪", "Testing — creating test cases..."),
            }
            icon, msg = phase_names[phase]
            _log(msg, status="running", icon=icon)
            status_text.markdown(f"**{icon} {msg}**")

            result = orchestrator.run_single_phase(phase, project_name, inputs)

            # Map phase output to results key
            key_map = {"ba": "user_stories", "design": "design_doc", "dev": "code", "test": "test_cases"}
            results[key_map[phase]] = result

            completed += 1
            progress_bar.progress(completed / total_phases)
            _log(f"{phase_names[phase][1].split('—')[0].strip()} complete ✅", status="success", icon="✅")

        # Execute tests if test cases were generated
        if "test_cases" in results and "code" in results:
            _log("⚡ Executing test cases...", status="running", icon="⚡")
            status_text.markdown("**⚡ Executing tests...**")
            test_exec_results = orchestrator.test_agent.execute_tests(
                test_code=results["test_cases"],
                source_code=results["code"],
                project_name=project_name,
            )
            results["test_results"] = test_exec_results
            p = test_exec_results.get("passed", 0)
            f = test_exec_results.get("failed", 0)
            _log(f"Tests executed: {p} passed, {f} failed", status="success" if f == 0 else "error", icon="🧪")

        st.session_state.pipeline_results = results
        _log(f"🎉 Pipeline complete! {len(phases)} phase(s) completed for '{project_name}'", status="success", icon="🎉")
        status_text.markdown("**🎉 Pipeline completed successfully!**")
        progress_bar.progress(1.0)

    except Exception as e:
        _log(f"Pipeline error: {str(e)}", status="error", icon="❌")
        status_text.markdown(f"**❌ Error: {str(e)}**")
        results["error"] = str(e)
        st.session_state.pipeline_results = results

    finally:
        st.session_state.pipeline_running = False
        st.rerun()
