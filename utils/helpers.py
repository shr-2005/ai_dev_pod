"""
Utility functions for the AI Dev Pod.
"""
import re
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional


def extract_code_blocks(markdown_text: str, language: str = None) -> List[str]:
    if language:
        pattern = rf"```{language}\n(.*?)```"
    else:
        pattern = r"```(?:\w+)?\n(.*?)```"
    blocks = re.findall(pattern, markdown_text, re.DOTALL)
    return [b.strip() for b in blocks if b.strip()]


def count_user_stories(user_stories_text: str) -> int:
    pattern = r"US-\d+"
    matches = re.findall(pattern, user_stories_text)
    return len(set(matches))


def extract_story_ids(text: str) -> List[str]:
    pattern = r"US-\d{3}"
    return sorted(list(set(re.findall(pattern, text))))


def extract_test_ids(text: str) -> List[str]:
    pattern = r"TC-\d{3}"
    return sorted(list(set(re.findall(pattern, text))))


def sanitize_project_name(name: str) -> str:
    return re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_").lower()


def truncate_text(text: str, max_chars: int = 500, suffix: str = "...") -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    return f"{hours:.1f}h"


def get_priority_color(priority: str) -> str:
    colors = {
        "high": "#ef4444",
        "medium": "#f59e0b",
        "low": "#22c55e",
    }
    return colors.get(priority.lower(), "#94a3b8")


def validate_env_config() -> dict:
    from dotenv import load_dotenv
    load_dotenv()

    issues = {}
    warnings = {}

    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or groq_key == "your_groq_api_key_here":
        issues["GROQ_API_KEY"] = "Not set. Required for LLM generation. Get free key at https://console.groq.com"

    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    if not hf_token or hf_token == "your_huggingface_token_here":
        warnings["HUGGINGFACEHUB_API_TOKEN"] = "Not set. Needed for MiniLM embeddings."

    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    if not Path(chroma_dir).exists():
        warnings["CHROMA_PERSIST_DIR"] = f"Directory {chroma_dir} will be created on first use."

    return {"issues": issues, "warnings": warnings, "valid": len(issues) == 0}


def create_project_summary(results: dict, project_name: str) -> str:
    lines = [f"# Project Summary: {project_name}", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

    if "user_stories" in results:
        count = count_user_stories(str(results["user_stories"]))
        lines.append(f"- **User Stories:** {count} stories generated")

    if "design_doc" in results:
        lines.append("- **Design Document:** Architecture, DB schema, and API design created")

    if "code" in results:
        lines.append("- **Code:** Production-ready implementation generated")

    if "test_cases" in results:
        tc_count = len(extract_test_ids(str(results["test_cases"])))
        lines.append(f"- **Test Cases:** {tc_count} test cases created")

    if "test_results" in results and isinstance(results["test_results"], dict):
        tr = results["test_results"]
        p, f = tr.get("passed", 0), tr.get("failed", 0)
        lines.append(f"- **Test Results:** {p} passed, {f} failed")

    return "\n".join(lines)