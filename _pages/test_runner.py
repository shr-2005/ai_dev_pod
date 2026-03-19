"""
Test Runner Page - View test cases and execute them with live output.
"""
import streamlit as st
from core.artifact_manager import get_artifact_manager


def render_test_runner():
    """Render the test runner page."""
    st.markdown("""
    <div class='main-header'>
        <h1>🧪 Test Runner</h1>
        <p>View generated test cases and execute automated tests</p>
    </div>
    """, unsafe_allow_html=True)

    results = st.session_state.get("pipeline_results", {})
    project_name = st.session_state.get("project_name", "project")

    tab1, tab2, tab3 = st.tabs(["🧪 Test Cases", "▶️ Run Tests", "📊 Test Report"])

    # ─── Tab 1: View Test Cases ────────────────────────────────────────
    with tab1:
        test_cases = results.get("test_cases")
        if not test_cases:
            st.info("No test cases generated yet. Run the pipeline with Testing phase enabled.")
            if st.button("🚀 Go to Pipeline", type="primary"):
                st.session_state.current_page = "pipeline"
                st.rerun()
        else:
            word_count = len(str(test_cases).split())
            st.metric("Test Case Document Size", f"{word_count} words")
            st.markdown("---")

            view_mode = st.radio(
                "View", ["📖 Rendered", "📝 Raw"], horizontal=True, label_visibility="collapsed"
            )
            if view_mode == "📖 Rendered":
                st.markdown(str(test_cases))
            else:
                st.code(str(test_cases), language="markdown")

            st.download_button(
                "⬇️ Download Test Cases",
                data=str(test_cases),
                file_name=f"{project_name}_test_cases.md",
                mime="text/markdown",
            )

    # ─── Tab 2: Run Tests ─────────────────────────────────────────────
    with tab2:
        st.markdown("### ▶️ Execute Automated Tests")

        code = results.get("code")
        test_cases = results.get("test_cases")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Source Code**")
            if code:
                st.success(f"✅ Code available ({len(str(code).split())} words)")
            else:
                st.warning("⚠️ No code generated yet")

        with col2:
            st.markdown("**Test Cases**")
            if test_cases:
                st.success(f"✅ Test cases available ({len(str(test_cases).split())} words)")
            else:
                st.warning("⚠️ No test cases generated yet")

        st.markdown("---")

        if code and test_cases:
            st.info(
                "🔧 **How it works:** The Testing Agent extracts Python test code from the generated "
                "test cases and runs them using pytest in an isolated environment. Results are parsed "
                "and displayed below."
            )

            if st.button("▶️ Run Tests Now", type="primary", use_container_width=False):
                with st.spinner("Running tests... this may take up to 60 seconds"):
                    from agents.test_agent import TestingAgent
                    agent = TestingAgent()
                    test_results = agent.execute_tests(
                        test_code=str(test_cases),
                        source_code=str(code),
                        project_name=project_name,
                    )
                    # Save to session
                    if "pipeline_results" not in st.session_state:
                        st.session_state.pipeline_results = {}
                    st.session_state.pipeline_results["test_results"] = test_results
                    st.rerun()

            # Show existing test results if available
            test_results = results.get("test_results")
            if test_results and isinstance(test_results, dict):
                _render_test_results(test_results)

        else:
            st.info("👉 Run the full pipeline first to generate code and test cases.")

        # Manual code input for testing
        with st.expander("🔧 Advanced: Test Custom Code"):
            st.markdown("Paste your own code and tests to run them directly.")
            custom_code = st.text_area("Source Code", height=200, placeholder="Paste Python code here...")
            custom_tests = st.text_area("Test Code (pytest)", height=200, placeholder="Paste pytest code here...")

            if st.button("▶️ Run Custom Tests") and custom_code and custom_tests:
                with st.spinner("Running custom tests..."):
                    from agents.test_agent import TestingAgent
                    agent = TestingAgent()
                    wrapped_tests = f"```python\n{custom_tests}\n```"
                    custom_results = agent.execute_tests(
                        test_code=wrapped_tests,
                        source_code=custom_code,
                        project_name=project_name,
                    )
                    _render_test_results(custom_results)

    # ─── Tab 3: Test Report ────────────────────────────────────────────
    with tab3:
        st.markdown("### 📊 Test Report")

        test_results = results.get("test_results")

        if not test_results or not isinstance(test_results, dict):
            st.info("No test execution results yet. Run tests in the **▶️ Run Tests** tab.")
        else:
            report = test_results.get("report", "No report generated.")
            st.markdown(report)

            # Saved reports from disk
            artifact_manager = get_artifact_manager()
            saved_reports = artifact_manager.list_artifacts("test_report")
            if saved_reports:
                st.markdown("---")
                st.markdown("**📁 Saved Test Reports**")
                for rep in saved_reports:
                    with st.expander(f"📄 {rep['filename']} — {rep['modified']}"):
                        content = artifact_manager.load("test_report", rep["filename"])
                        if content:
                            st.markdown(content)


def _render_test_results(test_results: dict):
    """Render test execution results as a visual summary."""
    st.markdown("### 📊 Execution Results")

    status = test_results.get("status", "unknown")
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    errors = test_results.get("errors", 0)
    skipped = test_results.get("skipped", 0)
    total = passed + failed + errors

    # Status banner
    if status == "completed" and failed == 0 and errors == 0 and total > 0:
        st.success(f"✅ All {total} tests passed!")
    elif status == "completed" and failed > 0:
        st.error(f"❌ {failed} test(s) failed out of {total} total.")
    elif status == "error":
        st.error("❌ Test execution encountered errors.")
    elif status == "timeout":
        st.warning("⏱️ Tests timed out.")
    else:
        st.info(f"ℹ️ Status: {status}")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✅ Passed", passed)
    col2.metric("❌ Failed", failed)
    col3.metric("🔴 Errors", errors)
    col4.metric("⏭️ Skipped", skipped)

    # Progress bar
    if total > 0:
        pass_rate = passed / total
        st.progress(pass_rate, text=f"Pass rate: {pass_rate*100:.1f}%")

    # Raw output
    output = test_results.get("output", "")
    if output:
        with st.expander("📋 Raw pytest Output"):
            st.code(output[:5000], language="text")
