"""Roadmap generation utilities for HireReady AI."""

import json
import re
from typing import Any, Dict, List

from openai import OpenAI


def normalize_skill(skill: str) -> str:
    if not skill:
        return ""
    return re.sub(r"\s+", " ", str(skill).strip())


RESOURCE_MAP = {
    "Python": "https://docs.python.org/3/tutorial/",
    "SQL": "https://www.postgresql.org/docs/",
    "FastAPI": "https://fastapi.tiangolo.com/",
    "Flask": "https://flask.palletsprojects.com/",
    "Docker": "https://docs.docker.com/",
    "REST API": "https://restfulapi.net/",
    "Git": "https://git-scm.com/doc",
    "AWS": "https://docs.aws.amazon.com/",
    "Azure": "https://learn.microsoft.com/azure/",
    "GCP": "https://cloud.google.com/docs",
    "Machine Learning": "https://scikit-learn.org/stable/",
    "LLM": "https://platform.openai.com/docs/guides/text-generation",
    "Kubernetes": "https://kubernetes.io/docs/",
    "React": "https://react.dev/learn",
    "JavaScript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "TypeScript": "https://www.typescriptlang.org/docs/",
    "PostgreSQL": "https://www.postgresql.org/docs/",
    "MySQL": "https://dev.mysql.com/doc/",
}


def build_week_resources(skills: List[str]) -> List[Dict[str, str]]:
    resources = []
    for skill in skills:
        url = RESOURCE_MAP.get(skill, "https://www.google.com/search?q=" + skill.replace(" ", "+"))
        resources.append({"title": f"{skill} learning resources", "url": url})
    return resources


def build_week_tasks(skills: List[str]) -> List[str]:
    tasks = []
    for skill in skills:
        tasks.append(f"Review the fundamentals of {skill} and take notes on key concepts.")
        tasks.append(f"Build a mini exercise or small project that uses {skill} in a practical scenario.")
        tasks.append(f"Validate your progress by testing the implementation, documenting results, and noting gaps.")
    return tasks


def generate_roadmap(missing_skills: List[str], job_description: str = "", api_key: str = None, model: str = None) -> Dict[str, Any]:
    """Generate a practical 4-6 week roadmap from missing skills."""
    normalized = [normalize_skill(skill) for skill in (missing_skills or []) if normalize_skill(skill)]
    if not normalized:
        normalized = ["Python", "SQL", "Docker", "REST API"]

    prioritized = sorted(set(normalized), key=lambda x: x.lower())

    if api_key and job_description:
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://localhost",
                    "X-OpenRouter-Title": "HireReady AI",
                },
            )

            prompt = f"""
Create a concise weekly learning roadmap based on these missing skills: {', '.join(prioritized)}.
Return valid JSON only with fields:
{{
  "title": "Roadmap title",
  "summary": "Short summary",
  "weeks": [
    {{
      "week": 1,
      "skills": ["skill1", "skill2"],
      "tasks": ["task1", "task2", "task3"],
      "resources": [{{"title": "Resource", "url": "https://..."}}]
    }}
  ]
}}
Job description: {job_description[:2500]}
"""
            response = client.chat.completions.create(
                model=model or "nvidia/nemotron-3-ultra-550b-a55b",
                messages=[
                    {"role": "system", "content": "You produce structured learning roadmaps in valid JSON format."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content
            if content:
                parsed = json.loads(content)
                weeks = parsed.get("weeks") or []
                if weeks:
                    return {
                        "title": parsed.get("title", "Career Roadmap"),
                        "summary": parsed.get("summary", "A structured learning plan to close the identified gaps."),
                        "hours_per_week": 8,
                        "weeks": weeks,
                    }
        except Exception:
            pass

    total_weeks = max(4, min(6, len(prioritized)))
    weeks = []

    for week_number in range(1, total_weeks + 1):
        start_index = (week_number - 1) * 2
        chunk = prioritized[start_index:start_index + 2]
        if not chunk:
            chunk = prioritized[:2]
        week_tasks = build_week_tasks(chunk)
        week_resources = build_week_resources(chunk)
        weeks.append({
            "week": week_number,
            "skills": chunk,
            "tasks": week_tasks,
            "resources": week_resources,
        })

    if len(weeks) < 4:
        while len(weeks) < 4:
            weeks.append({
                "week": len(weeks) + 1,
                "skills": [prioritized[0] if prioritized else "Python"],
                "tasks": [
                    "Review the core concepts and identify the smallest viable project for this skill.",
                    "Implement a focused exercise and document what you learned.",
                    "Reflect on the gaps and define the next improvement area."
                ],
                "resources": [
                    {"title": "General learning guide", "url": "https://www.google.com/search?q=" + (prioritized[0] if prioritized else "Python")}
                ],
            })

    return {
        "title": "Career Readiness Roadmap",
        "summary": "A structured plan to close the most important skill gaps for your target role.",
        "hours_per_week": 8,
        "weeks": weeks,
    }
