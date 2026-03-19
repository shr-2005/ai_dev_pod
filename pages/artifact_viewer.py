"""
Artifact Viewer Page - View and download generated artifacts.
"""
import streamlit as st
from pathlib import Path
from core.artifact_manager import get_artifact_manager


def render_artifact_viewer(artifact_type: str, page_title: str):
    """
    Generic artifact viewer for any artifact type.
    
    Args:
        artifact_type: One of 'user_stories', 'design_doc', 'code', 'test_cases'
        page_title: Display title for the page
    """
    st.markdown(f"""
    <div class='main-header'>
        <h1>{page_title}</h1>
        <p>View, explore and download generated artifacts</p>
    </div>
    """, unsafe_allow_html=True)

    artifact_manager = get_artifact_manager()

    # Check session state first (fresh from pipeline)
    results = st.session_state.get("pipeline_results", {})
    session_content = results.get(artifact_type)

    # Tabs: Current Session | Saved Files
    tab1, tab2 = st.tabs(["📄 Current Session", "📁 Saved Files"])

    with tab1:
        _render_session_artifact(artifact_type, page_title, session_content)

    with tab2:
        _render_saved_artifacts(artifact_type, artifact_manager)


def _render_session_artifact(artifact_type: str, page_title: str, content):
    """Render the artifact from the current pipeline session."""
    if not content:
        st.info(
            f"No {page_title.split(' ', 1)[-1].lower()} generated in current session.\n\n"
            "👉 Run the pipeline from **🚀 Run Pipeline** first."
        )
        if st.button("🚀 Go to Pipeline Runner", type="primary"):
            st.session_state.current_page = "pipeline"
            st.rerun()
        return

    content_str = str(content)
    project_name = st.session_state.get("project_name", "project")

    # Stats
    word_count = len(content_str.split())
    line_count = content_str.count("\n")
    char_count = len(content_str)

    col1, col2, col3 = st.columns(3)
    col1.metric("Words", f"{word_count:,}")
    col2.metric("Lines", f"{line_count:,}")
    col3.metric("Characters", f"{char_count:,}")

    st.markdown("---")

    # View mode
    view_mode = st.radio(
        "View Mode",
        ["📖 Rendered (Markdown)", "📝 Raw Text"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # Content display
    if view_mode == "📖 Rendered (Markdown)":
        with st.container():
            st.markdown(content_str)
    else:
        st.code(content_str, language="markdown")

    # Download
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        safe_name = "".join(c if c.isalnum() else "_" for c in project_name)
        st.download_button(
            label=f"⬇️ Download {artifact_type.replace('_', ' ').title()}",
            data=content_str,
            file_name=f"{safe_name}_{artifact_type}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        # Copy to clipboard workaround
        st.download_button(
            label="⬇️ Download as TXT",
            data=content_str,
            file_name=f"{safe_name}_{artifact_type}.txt",
            mime="text/plain",
            use_container_width=True,
        )


def _render_saved_artifacts(artifact_type: str, artifact_manager):
    """Render list of saved artifacts from disk."""
    artifacts = artifact_manager.list_artifacts(artifact_type)

    if not artifacts:
        st.info("No saved artifacts found. Run the pipeline to generate artifacts.")
        return

    st.markdown(f"**{len(artifacts)} saved artifact(s)**")

    for artifact in artifacts:
        with st.expander(f"📄 {artifact['filename']} — {artifact['modified']}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.text(f"Size: {artifact['size']} bytes")
            col2.text(f"Modified: {artifact['modified']}")

            if col3.button("👁️ Load", key=f"load_{artifact['filename']}"):
                content = artifact_manager.load(artifact_type, artifact["filename"])
                if content:
                    st.markdown(content)
                else:
                    st.error("Could not load file.")

            # Quick download
            content = artifact_manager.load(artifact_type, artifact["filename"])
            if content:
                st.download_button(
                    label="⬇️ Download",
                    data=content,
                    file_name=artifact["filename"],
                    mime="text/markdown",
                    key=f"dl_{artifact['filename']}",
                )
