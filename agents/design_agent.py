"""
Design Agent - Creates software architecture and design documents.
"""
from typing import Optional
from core.llm_client import LlamaClient
from core.vector_store import get_vector_store
from core.artifact_manager import get_artifact_manager


class DesignAgent:
    """
    Design Agent: Transforms user stories into software architecture and detailed design docs.
    Produces system design, database schema, API contracts, and component diagrams (textual).
    """

    SYSTEM_PROMPT = """You are a senior Software Architect in a development team.
Your responsibility is to create comprehensive software design documents.

You produce:
1. System Architecture Overview (components, layers, interactions)
2. Database Design (tables, relationships, key fields)
3. API Design (endpoints, methods, request/response schemas)
4. Component Diagrams (described in structured text/pseudo-UML)
5. Technology Stack decisions with justification
6. Non-functional requirements (scalability, security, performance)

Be precise, technical, and follow industry best practices.
Output clean, professional Markdown with clear sections."""

    def __init__(self):
        self.llm = LlamaClient()
        self.vector_store = get_vector_store()
        self.artifact_manager = get_artifact_manager()
        self.name = "Design Agent"
        self.role = "design_agent"

    def create_design(
        self,
        user_stories: str,
        project_name: str,
        tech_preferences: Optional[str] = None,
        template: Optional[str] = None,
    ) -> str:
        """
        Create software design document from user stories.
        
        Args:
            user_stories: The generated user stories
            project_name: Name of the project
            tech_preferences: Optional technology preferences
            template: Optional design template
            
        Returns:
            Design document in Markdown format
        """
        if template is None:
            template = self.vector_store.get_template("design_doc", query=user_stories[:300])

        template_section = f"\n\nDesign template:\n{template}\n" if template else ""

        tech_section = (
            f"\n\nTechnology preferences:\n{tech_preferences}" if tech_preferences else ""
        )

        prompt = f"""Project Name: {project_name}

User Stories to Design For:
{user_stories[:3000]}
{tech_section}
{template_section}

Create a comprehensive Software Design Document with these sections:

## 1. Executive Summary
Brief overview of the system.

## 2. System Architecture
- Architecture pattern (MVC, Microservices, Layered, etc.)
- High-level component diagram (text-based)
- Data flow description

## 3. Technology Stack
- Frontend, Backend, Database, DevOps tools with justification

## 4. Database Design
- Entity-Relationship overview
- Main tables with key columns
- Relationships and constraints

## 5. API Design
- REST API endpoints
- Request/Response formats (JSON examples)
- Authentication approach

## 6. Component Design
- Key modules and their responsibilities
- Inter-component communication

## 7. Security Design
- Authentication/Authorization approach
- Data protection measures

## 8. Non-Functional Requirements
- Scalability approach
- Performance targets
- Availability requirements

Format as professional Markdown."""

        response = self.llm.generate(prompt, system_prompt=self.SYSTEM_PROMPT, max_new_tokens=2048)

        filepath = self.artifact_manager.save(
            artifact_type="design_doc",
            content=response,
            project_name=project_name,
            metadata={"agent": self.name, "status": "generated"},
        )

        self.vector_store.add_artifact(
            artifact_id=f"design_doc_{project_name}",
            artifact_type="design_doc",
            content=response,
            metadata={"project": project_name, "filepath": filepath},
        )

        return response

    def create_component_design(
        self, user_story: str, project_name: str, design_context: str = ""
    ) -> str:
        """Create detailed design for a specific component/user story."""
        prompt = f"""Project: {project_name}

User Story:
{user_story}

System Design Context:
{design_context[:1000] if design_context else 'No prior context'}

Create a detailed component design including:
1. Class/Module structure
2. Key methods/functions with signatures
3. Data models
4. Error handling approach
5. Unit test considerations"""

        response = self.llm.generate(prompt, system_prompt=self.SYSTEM_PROMPT, max_new_tokens=1024)
        return response

    def get_status(self) -> dict:
        """Get agent status."""
        latest = self.artifact_manager.get_latest("design_doc")
        return {
            "agent": self.name,
            "status": "ready",
            "artifacts_created": len(self.artifact_manager.list_artifacts("design_doc")),
            "latest_artifact": latest["filename"] if latest else None,
        }
