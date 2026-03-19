"""
PM Chat Page - Conversational interface with the AI Project Lead.
"""
import streamlit as st
from datetime import datetime


def render_pm_chat():
    """Render the Project Manager chat interface."""
    st.markdown("""
    <div class='main-header'>
        <h1>💬 Project Manager Chat</h1>
        <p>Chat with the AI Project Lead to check status, quality, and artifact details</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    results = st.session_state.get("pipeline_results", {})
    project_name = st.session_state.get("project_name", "")

    # Sidebar context panel
    col_chat, col_context = st.columns([3, 1])

    with col_context:
        st.markdown("**📌 Quick Questions**")
        quick_questions = [
            "What is the project status?",
            "How many user stories were created?",
            "What is the overall architecture?",
            "How many tests passed?",
            "What are the high priority user stories?",
            "Summarize the design document",
            "What technology stack is being used?",
            "Are there any test failures?",
        ]
        for q in quick_questions:
            if st.button(q, key=f"quick_{q[:20]}", use_container_width=True):
                st.session_state._pending_message = q
                st.rerun()

        st.markdown("---")
        st.markdown("**📊 Context Available**")
        context_items = {
            "User Stories": "user_stories",
            "Design Doc": "design_doc",
            "Code": "code",
            "Test Cases": "test_cases",
        }
        for label, key in context_items.items():
            has = key in results and results[key]
            icon = "🟢" if has else "🔴"
            st.markdown(f"{icon} {label}", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.chat_history = []
            st.rerun()

    with col_chat:
        # Welcome message
        if not st.session_state.chat_messages:
            project_info = f" for **{project_name}**" if project_name else ""
            has_artifacts = any(key in results for key in ["user_stories", "design_doc", "code"])
            artifact_note = (
                " I have full context of the generated user stories, design document, code, and test results."
                if has_artifacts
                else " No pipeline has been run yet — run the pipeline first to give me project context."
            )

            welcome = {
                "role": "assistant",
                "content": f"👋 Hello! I'm the **AI Project Lead** of this Virtual Development Pod{project_info}.{artifact_note}\n\nAsk me anything about the project — artifact quality, test status, design decisions, or anything else!",
                "time": datetime.now().strftime("%H:%M"),
            }
            st.session_state.chat_messages.append(welcome)

        # Render chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                _render_message(msg)

        # Handle pending message (from quick questions)
        if hasattr(st.session_state, "_pending_message"):
            user_msg = st.session_state._pending_message
            del st.session_state._pending_message
            _process_message(user_msg, results, project_name)
            st.rerun()

        # Input
        st.markdown("---")
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_send = st.columns([5, 1])
            with col_input:
                user_input = st.text_input(
                    "Message",
                    placeholder="Ask the Project Lead anything...",
                    label_visibility="collapsed",
                )
            with col_send:
                send = st.form_submit_button("Send", use_container_width=True, type="primary")

        if send and user_input.strip():
            _process_message(user_input.strip(), results, project_name)
            st.rerun()


def _render_message(msg: dict):
    """Render a single chat message."""
    role = msg["role"]
    content = msg["content"]
    time_str = msg.get("time", "")

    if role == "user":
        st.markdown(
            f"""<div style='background:#1e3a5f; border-left:3px solid #3b82f6; padding:0.8rem 1rem;
            border-radius:0 8px 8px 0; margin:0.5rem 0;'>
            <div style='color:#93c5fd; font-size:0.75rem; margin-bottom:0.3rem;'>👤 Project Manager · {time_str}</div>
            <div style='color:#e2e8f0;'>{content}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div style='background:#1e2d3d; border-left:3px solid #6366f1; padding:0.8rem 1rem;
            border-radius:0 8px 8px 0; margin:0.5rem 0;'>
            <div style='color:#a5b4fc; font-size:0.75rem; margin-bottom:0.3rem;'>🤖 AI Project Lead · {time_str}</div>
            <div style='color:#e2e8f0;'>{content}</div>
            </div>""",
            unsafe_allow_html=True,
        )


def _process_message(user_input: str, results: dict, project_name: str):
    """Process a user message and generate AI response."""
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%H:%M"),
    })

    # Build context from pipeline results
    context_parts = []
    if project_name:
        context_parts.append(f"Project: {project_name}")

    if "user_stories" in results and results["user_stories"]:
        us_preview = str(results["user_stories"])[:800]
        context_parts.append(f"User Stories (preview):\n{us_preview}")

    if "design_doc" in results and results["design_doc"]:
        dd_preview = str(results["design_doc"])[:600]
        context_parts.append(f"Design Document (preview):\n{dd_preview}")

    if "test_results" in results and isinstance(results["test_results"], dict):
        tr = results["test_results"]
        context_parts.append(
            f"Test Results: {tr.get('passed', 0)} passed, {tr.get('failed', 0)} failed, "
            f"status={tr.get('status', 'unknown')}"
        )

    if "code" in results and results["code"]:
        code_preview = str(results["code"])[:400]
        context_parts.append(f"Generated Code (preview):\n{code_preview}")

    context_str = "\n\n".join(context_parts) if context_parts else "No pipeline data available yet."

    # Build conversation history for LLM
    llm_history = []
    for msg in st.session_state.chat_messages[:-1]:  # exclude the message we just added
        llm_history.append({"role": msg["role"], "content": msg["content"]})

    # Generate response
    response = _generate_chat_response(user_input, context_str, llm_history, project_name)

    # Add assistant response
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": response,
        "time": datetime.now().strftime("%H:%M"),
    })

    # Update LLM history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})


def _generate_chat_response(user_input: str, context: str, history: list, project_name: str) -> str:
    """Generate a chat response using the LLM."""
    try:
        from core.llm_client import LlamaClient
        client = LlamaClient()

        system_prompt = f"""You are the AI Project Lead of a Virtual Development Pod.
You oversee: Business Analyst Agent, Design Agent, Developer Agent, and Testing Agent.
Your role: Answer the Project Manager's questions about project status, artifacts, and quality.

Project Context:
{context}

Instructions:
- Be concise and professional
- Reference specific details from the context when relevant
- If asked about something not in context, say so honestly
- Format responses clearly with bullets or headers when helpful
- Keep responses under 300 words unless a detailed breakdown is requested"""

        enriched_input = f"[Project Context Available: {bool(context and 'No pipeline' not in context)}]\n\nPM Question: {user_input}"

        response = client.generate(
            prompt=enriched_input,
            system_prompt=system_prompt,
            max_new_tokens=512,
            temperature=0.6,
        )

        if not response or response.startswith("Error"):
            return _fallback_response(user_input, context, project_name)

        return response

    except Exception as e:
        return _fallback_response(user_input, context, project_name)


def _fallback_response(user_input: str, context: str, project_name: str) -> str:
    """Provide a rule-based fallback response when LLM is unavailable."""
    q = user_input.lower()
    has_context = "No pipeline" not in context

    if not has_context:
        return (
            "⚠️ No pipeline has been run yet. Please go to **🚀 Run Pipeline** first to generate "
            "project artifacts. Once the pipeline completes, I'll have full context to answer your questions."
        )

    if any(w in q for w in ["status", "progress", "done", "complete"]):
        phases = []
        if "User Stories" in context:
            phases.append("✅ User Stories")
        if "Design Document" in context:
            phases.append("✅ Design Document")
        if "Generated Code" in context:
            phases.append("✅ Code")
        if "Test Results" in context:
            phases.append("✅ Tests")
        phase_str = "\n".join(phases) if phases else "No phases completed yet."
        return f"**Project Status for '{project_name}':**\n\n{phase_str}\n\nAll completed phases have artifacts available in the sidebar."

    if any(w in q for w in ["test", "pass", "fail"]):
        if "Test Results:" in context:
            for line in context.split("\n"):
                if "Test Results:" in line:
                    return f"**Test Execution Results:**\n\n{line}\n\nView the full report in the 🧪 Test Runner page."
        return "Test results are not available yet. Run the pipeline with the Testing phase enabled."

    if any(w in q for w in ["user stor", "us-", "epic", "requirement"]):
        return (
            f"The Business Analyst Agent generated user stories for **{project_name}**. "
            "View the full document in **📋 User Stories** in the sidebar. "
            "Stories follow the format: 'As a [user], I want [action], so that [benefit]' with acceptance criteria and story points."
        )

    if any(w in q for w in ["design", "architecture", "database", "api"]):
        return (
            f"The Design Agent created a software design document for **{project_name}**. "
            "It includes system architecture, database schema, API design, and technology stack decisions. "
            "View the full document in **🏗️ Design Doc** in the sidebar."
        )

    if any(w in q for w in ["code", "implement", "develop", "python"]):
        return (
            f"The Developer Agent generated code for **{project_name}**. "
            "View the full implementation in **💻 Code** in the sidebar. "
            "The code follows best practices with docstrings, error handling, and type hints."
        )

    return (
        f"I'm the AI Project Lead for **{project_name}**. "
        "I can help you with: project status, artifact reviews, test results, design questions, and code quality. "
        "Note: LLM API may be unavailable — check your HF_TOKEN in the .env file. "
        "In the meantime, explore artifacts using the sidebar navigation."
    )
