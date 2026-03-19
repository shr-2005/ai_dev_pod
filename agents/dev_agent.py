"""
Developer Agent - Generates production-ready code from user stories and design documents.
"""
from typing import Optional
from core.llm_client import LlamaClient
from core.vector_store import get_vector_store
from core.artifact_manager import get_artifact_manager


class DeveloperAgent:
    """
    Developer Agent: Generates well-structured, documented code based on
    user stories and design documents.
    """

    SYSTEM_PROMPT = """You are a senior software developer specializing in clean, production-ready code.

Your coding standards:
1. Write clean, readable, well-commented code
2. Follow SOLID principles and design patterns
3. Include proper error handling and validation
4. Add docstrings/comments for all classes and functions
5. Follow language-specific conventions (PEP8 for Python, etc.)
6. Write modular, testable code
7. Include type hints (Python) or type annotations
8. Handle edge cases explicitly

Always produce complete, runnable code — not pseudocode or snippets unless asked."""

    def __init__(self):
        self.llm = LlamaClient()
        self.vector_store = get_vector_store()
        self.artifact_manager = get_artifact_manager()
        self.name = "Developer Agent"
        self.role = "dev_agent"

    def generate_code(
        self,
        user_stories: str,
        design_doc: str,
        project_name: str,
        language: str = "Python",
        framework: Optional[str] = None,
        specific_story: Optional[str] = None,
    ) -> str:
        """
        Generate code from user stories and design document.
        
        Args:
            user_stories: The user stories to implement
            design_doc: The software design document
            project_name: Name of the project
            language: Programming language to use
            framework: Optional framework (Flask, Django, FastAPI, etc.)
            specific_story: Optionally focus on a specific story
            
        Returns:
            Generated code as a string
        """
        framework_text = f" using {framework}" if framework else ""

        if specific_story:
            focus = f"\nFocus specifically on implementing this user story:\n{specific_story}\n"
            stories_text = focus
        else:
            stories_text = f"\nUser Stories to implement:\n{user_stories[:2000]}\n"

        prompt = f"""Project: {project_name}
Language: {language}{framework_text}

{stories_text}

Design Reference:
{design_doc[:1500] if design_doc else 'No design document available'}

Generate complete {language} code{framework_text} that implements the user stories above.

Include:
1. Complete file structure (show file paths as comments)
2. Model/Entity classes with validation
3. Service layer with business logic
4. API routes/controllers (if applicable)
5. Database integration code (if applicable)
6. Utility functions
7. Configuration management
8. Comprehensive error handling
9. Logging setup
10. Main entry point

Make the code production-ready with full docstrings and type hints."""

        response = self.llm.generate(prompt, system_prompt=self.SYSTEM_PROMPT, max_new_tokens=2048)

        filepath = self.artifact_manager.save(
            artifact_type="code",
            content=response,
            project_name=project_name,
            metadata={
                "agent": self.name,
                "language": language,
                "framework": framework or "None",
                "status": "generated",
            },
        )

        self.vector_store.add_artifact(
            artifact_id=f"code_{project_name}",
            artifact_type="code",
            content=response,
            metadata={"project": project_name, "language": language, "filepath": filepath},
        )

        return response

    def generate_module(
        self,
        module_name: str,
        requirements: str,
        project_name: str,
        language: str = "Python",
        existing_code_context: str = "",
    ) -> str:
        """Generate a specific module or component."""
        prompt = f"""Project: {project_name}
Module: {module_name}
Language: {language}

Module Requirements:
{requirements}

Existing Code Context:
{existing_code_context[:1000] if existing_code_context else 'None'}

Write the complete {module_name} module with:
1. Full implementation
2. All necessary imports
3. Docstrings for all public methods
4. Error handling
5. Example usage in the docstring"""

        return self.llm.generate(prompt, system_prompt=self.SYSTEM_PROMPT, max_new_tokens=1024)

    def review_code(self, code: str, project_name: str) -> str:
        """Review generated code and suggest improvements."""
        review_prompt = """You are a senior code reviewer. Review the provided code for:
1. Code quality and readability
2. Security vulnerabilities
3. Performance issues
4. Best practices violations
5. Missing error handling
6. Test coverage gaps

Provide specific, actionable feedback with line references where possible."""

        prompt = f"""Code to Review (Project: {project_name}):

{code[:3000]}

Provide a detailed code review with:
- Overall assessment (score 1-10)
- Critical issues
- Major improvements
- Minor suggestions
- Security concerns
- Performance notes"""

        return self.llm.generate(prompt, system_prompt=review_prompt, max_new_tokens=1024)

    def get_status(self) -> dict:
        """Get agent status."""
        latest = self.artifact_manager.get_latest("code")
        return {
            "agent": self.name,
            "status": "ready",
            "artifacts_created": len(self.artifact_manager.list_artifacts("code")),
            "latest_artifact": latest["filename"] if latest else None,
        }
