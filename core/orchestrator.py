"""
Project Lead Orchestrator - Manages the entire AI development pod pipeline.
Uses CrewAI to orchestrate agents through the full SDLC.
"""
import os
from typing import Optional, Dict, Callable
from datetime import datetime

from crewai import Agent, Task, Crew, Process
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv

from agents.ba_agent import BusinessAnalystAgent
from agents.design_agent import DesignAgent
from agents.dev_agent import DeveloperAgent
from agents.test_agent import TestingAgent
from core.artifact_manager import get_artifact_manager
from core.vector_store import get_vector_store

load_dotenv()


class ProjectLeadOrchestrator:
    """
    Orchestrates the full development lifecycle using CrewAI.
    Coordinates: BA Agent → Design Agent → Dev Agent → Test Agent
    """

    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
        self.model_name = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")

        # Direct agent instances (used for standalone calls)
        self.ba_agent = BusinessAnalystAgent()
        self.design_agent = DesignAgent()
        self.dev_agent = DeveloperAgent()
        self.test_agent = TestingAgent()

        self.artifact_manager = get_artifact_manager()
        self.vector_store = get_vector_store()

        # Pipeline state
        self.pipeline_state: Dict = {
            "project_name": None,
            "status": "idle",
            "current_phase": None,
            "phases_completed": [],
            "artifacts": {},
            "started_at": None,
            "completed_at": None,
        }

    def _get_llm(self):
        """Get the HuggingFace LLM for CrewAI."""
        return HuggingFaceEndpoint(
            repo_id=self.model_name,
            huggingfacehub_api_token=self.hf_token,
            max_new_tokens=1024,
            temperature=0.7,
        )

    def run_full_pipeline(
        self,
        business_requirements: str,
        project_name: str,
        language: str = "Python",
        framework: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Dict:
        """
        Run the full development pipeline end-to-end.
        
        Args:
            business_requirements: High-level requirements
            project_name: Project name
            language: Target programming language
            framework: Optional framework
            progress_callback: Optional callback(phase, message) for progress updates
            
        Returns:
            Dict with all generated artifacts
        """
        def update(phase: str, msg: str):
            self.pipeline_state["current_phase"] = phase
            if progress_callback:
                progress_callback(phase, msg)

        self.pipeline_state.update({
            "project_name": project_name,
            "status": "running",
            "phases_completed": [],
            "started_at": datetime.now().isoformat(),
        })

        results = {}

        try:
            # Phase 1: Business Analysis
            update("ba", f"📋 BA Agent analyzing requirements for '{project_name}'...")
            user_stories = self.ba_agent.generate_user_stories(
                business_requirements=business_requirements,
                project_name=project_name,
            )
            results["user_stories"] = user_stories
            self.pipeline_state["phases_completed"].append("business_analysis")
            self.pipeline_state["artifacts"]["user_stories"] = user_stories
            update("ba", "✅ User stories generated successfully!")

            # Phase 2: Design
            update("design", "🏗️ Design Agent creating software architecture...")
            design_doc = self.design_agent.create_design(
                user_stories=user_stories,
                project_name=project_name,
                tech_preferences=f"Language: {language}" + (f", Framework: {framework}" if framework else ""),
            )
            results["design_doc"] = design_doc
            self.pipeline_state["phases_completed"].append("design")
            self.pipeline_state["artifacts"]["design_doc"] = design_doc
            update("design", "✅ Design document created!")

            # Phase 3: Development
            update("dev", "💻 Developer Agent generating code...")
            code = self.dev_agent.generate_code(
                user_stories=user_stories,
                design_doc=design_doc,
                project_name=project_name,
                language=language,
                framework=framework,
            )
            results["code"] = code
            self.pipeline_state["phases_completed"].append("development")
            self.pipeline_state["artifacts"]["code"] = code
            update("dev", "✅ Code generated!")

            # Phase 4: Testing
            update("test", "🧪 Testing Agent creating and running tests...")
            test_cases = self.test_agent.generate_test_cases(
                user_stories=user_stories,
                code=code,
                project_name=project_name,
            )
            results["test_cases"] = test_cases
            self.pipeline_state["phases_completed"].append("test_generation")
            self.pipeline_state["artifacts"]["test_cases"] = test_cases
            update("test", "⚡ Executing tests...")

            # Execute tests
            test_results = self.test_agent.execute_tests(
                test_code=test_cases,
                source_code=code,
                project_name=project_name,
            )
            results["test_results"] = test_results
            self.pipeline_state["phases_completed"].append("test_execution")
            self.pipeline_state["artifacts"]["test_results"] = test_results

            status_msg = f"✅ Tests done — {test_results['passed']} passed, {test_results['failed']} failed"
            update("test", status_msg)

            self.pipeline_state["status"] = "completed"
            self.pipeline_state["completed_at"] = datetime.now().isoformat()
            update("complete", "🎉 Full pipeline completed successfully!")

        except Exception as e:
            self.pipeline_state["status"] = "error"
            self.pipeline_state["error"] = str(e)
            update("error", f"❌ Pipeline error: {str(e)}")
            results["error"] = str(e)

        return results

    def run_single_phase(
        self,
        phase: str,
        project_name: str,
        inputs: Dict,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Run a single phase of the pipeline.
        
        Args:
            phase: One of 'ba', 'design', 'dev', 'test'
            project_name: Project name
            inputs: Phase-specific inputs
            progress_callback: Optional progress callback
            
        Returns:
            Generated artifact content
        """
        def update(msg: str):
            if progress_callback:
                progress_callback(phase, msg)

        if phase == "ba":
            update("📋 Generating user stories...")
            result = self.ba_agent.generate_user_stories(
                business_requirements=inputs.get("requirements", ""),
                project_name=project_name,
            )
            update("✅ User stories ready!")
            return result

        elif phase == "design":
            update("🏗️ Creating design document...")
            result = self.design_agent.create_design(
                user_stories=inputs.get("user_stories", ""),
                project_name=project_name,
                tech_preferences=inputs.get("tech_preferences"),
            )
            update("✅ Design document ready!")
            return result

        elif phase == "dev":
            update("💻 Generating code...")
            result = self.dev_agent.generate_code(
                user_stories=inputs.get("user_stories", ""),
                design_doc=inputs.get("design_doc", ""),
                project_name=project_name,
                language=inputs.get("language", "Python"),
                framework=inputs.get("framework"),
            )
            update("✅ Code generated!")
            return result

        elif phase == "test":
            update("🧪 Generating test cases...")
            result = self.test_agent.generate_test_cases(
                user_stories=inputs.get("user_stories", ""),
                code=inputs.get("code", ""),
                project_name=project_name,
            )
            update("✅ Test cases ready!")
            return result

        else:
            raise ValueError(f"Unknown phase: {phase}. Use 'ba', 'design', 'dev', or 'test'.")

    def get_pipeline_status(self) -> Dict:
        """Get the current pipeline status."""
        agent_statuses = {
            "BA Agent": self.ba_agent.get_status(),
            "Design Agent": self.design_agent.get_status(),
            "Developer Agent": self.dev_agent.get_status(),
            "Testing Agent": self.test_agent.get_status(),
        }

        return {
            "pipeline": self.pipeline_state,
            "agents": agent_statuses,
            "artifacts_summary": self.artifact_manager.get_summary(),
        }

    def chat_response(self, conversation_history: list, user_message: str) -> str:
        """
        Generate a chat response as the Project Lead.
        Combines pipeline status awareness with LLM response.
        """
        from core.llm_client import LlamaClient
        client = LlamaClient()

        # Build context from pipeline state and latest artifacts
        status = self.get_pipeline_status()
        context = f"""
Current Pipeline State: {self.pipeline_state['status']}
Phases Completed: {', '.join(self.pipeline_state['phases_completed']) or 'None yet'}
Project: {self.pipeline_state.get('project_name', 'Not started')}
Artifact Summary: {status['artifacts_summary']}
"""

        # Prepend context to history
        system_context = f"""You are the AI Project Lead of the Virtual Development Pod.
You manage: BA Agent, Design Agent, Developer Agent, and Testing Agent.

Current project context:
{context}

Answer questions about project status, artifact quality, and agent outputs.
Be specific and reference actual data when available."""

        return client.chat(conversation_history, f"[Context: {context}]\n\nPM Question: {user_message}")
