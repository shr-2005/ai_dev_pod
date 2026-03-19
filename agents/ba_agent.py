"""
Business Analyst Agent - Creates user stories from high-level business requirements.
"""
from typing import Optional
from core.llm_client import LlamaClient
from core.vector_store import get_vector_store
from core.artifact_manager import get_artifact_manager


class BusinessAnalystAgent:
    """
    BA Agent: Analyzes business requirements and generates structured user stories
    following standard Agile format with acceptance criteria.
    """

    SYSTEM_PROMPT = """You are a senior Business Analyst in a software development team.
Your role is to transform high-level business requirements into clear, structured user stories.

Follow these rules strictly:
1. Use the format: "As a [user type], I want to [action], so that [benefit]"
2. Each story must have a title, description, acceptance criteria (3-5 items), and priority
3. Group related stories under epics
4. Be specific and testable — no vague language
5. Include edge cases and non-functional requirements as separate stories
6. Number all user stories (US-001, US-002, etc.)
7. Output well-formatted Markdown"""

    def __init__(self):
        self.llm = LlamaClient()
        self.vector_store = get_vector_store()
        self.artifact_manager = get_artifact_manager()
        self.name = "Business Analyst Agent"
        self.role = "ba_agent"

    def generate_user_stories(
        self,
        business_requirements: str,
        project_name: str,
        template: Optional[str] = None,
    ) -> str:
        """
        Generate user stories from business requirements.
        
        Args:
            business_requirements: The high-level business requirements text
            project_name: Name of the project
            template: Optional template to follow
            
        Returns:
            Generated user stories in Markdown format
        """
        # Retrieve template from vector store
        if template is None:
            template = self.vector_store.get_template("user_stories", query=business_requirements)

        template_section = ""
        if template:
            template_section = f"\n\nOrganization template to follow:\n{template}\n"

        prompt = f"""Project Name: {project_name}

Business Requirements:
{business_requirements}
{template_section}

Generate comprehensive user stories for this project. Include:
1. Project overview section
2. Epics (major feature groups)
3. Individual user stories under each epic (at least 8-12 stories total)
4. Acceptance criteria for each story
5. Story points estimate (1, 2, 3, 5, 8)
6. Priority (High/Medium/Low)
7. Dependencies between stories where relevant

Format everything as clean, professional Markdown."""

        response = self.llm.generate(prompt, system_prompt=self.SYSTEM_PROMPT, max_new_tokens=2048)

        # Save artifact
        filepath = self.artifact_manager.save(
            artifact_type="user_stories",
            content=response,
            project_name=project_name,
            metadata={"agent": self.name, "status": "generated"},
        )

        # Store in vector store for retrieval
        self.vector_store.add_artifact(
            artifact_id=f"user_stories_{project_name}",
            artifact_type="user_stories",
            content=response,
            metadata={"project": project_name, "filepath": filepath},
        )

        return response

    def refine_user_stories(self, existing_stories: str, feedback: str, project_name: str) -> str:
        """Refine existing user stories based on feedback."""
        prompt = f"""Existing User Stories:
{existing_stories}

Feedback from Project Manager:
{feedback}

Please refine and update the user stories based on this feedback. 
Maintain the same format but incorporate all feedback points.
Mark updated stories with [UPDATED] and new stories with [NEW]."""

        response = self.llm.generate(prompt, system_prompt=self.SYSTEM_PROMPT, max_new_tokens=2048)

        self.artifact_manager.save(
            artifact_type="user_stories",
            content=response,
            project_name=project_name,
            metadata={"agent": self.name, "status": "refined", "version": "v2"},
        )

        return response

    def get_status(self) -> dict:
        """Get agent status and artifact count."""
        latest = self.artifact_manager.get_latest("user_stories")
        return {
            "agent": self.name,
            "status": "ready",
            "artifacts_created": len(self.artifact_manager.list_artifacts("user_stories")),
            "latest_artifact": latest["filename"] if latest else None,
        }
