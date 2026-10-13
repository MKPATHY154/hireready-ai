"""Skill-gap analysis for HireReady AI.

This module compares a candidate's extracted resume skills with the required skills in a job description,
then categorizes matches, missing required skills, and gap summary.
It includes a fallback heuristic to work even when the AI API is not available or fails.
"""

import json
import re
from typing import Any, Dict, List, Tuple

from openai import OpenAI

from resume_parser import SKILLS


def normalize_skill(skill: str) -> str:
    """Normalize skill names for consistent comparison."""
    if not skill:
        return ""
    cleaned = re.sub(r"\s+", " ", skill.strip())
    return cleaned


def find_matching_skills(resume_skills: List[str], job_skills: List[str]) -> List[str]:
    """Return the skills present in both resume and job descriptions."""
    resume_lookup = {normalize_skill(s).lower(): normalize_skill(s) for s in resume_skills}
    matches = []
    for skill in job_skills:
        normalized = normalize_skill(skill)
        if normalized.lower() in resume_lookup:
            matches.append(normalized)
    return sorted(set(matches), key=lambda x: x.lower())


def get_job_skill_fallback(job_description: str) -> Dict[str, List[str]]:
    """Fallback rule-based extraction of skills from a job description."""
    text = job_description.lower()
    found = []
    for skill in SKILLS:
        if skill.lower() in text:
            found.append(skill)

    required = []
    preferred = []
    strong_required_keywords = [
        "python", "sql", "rest api", "flask", "fastapi", "docker", "machine learning",
        "deep learning", "aws", "gcp", "azure", "llm", "rag", "streamlit", "pandas",
        "numpy", "pytorch", "tensorflow", "git", "postgresql", "mysql"
    ]
    preferred_keywords = [
        "kubernetes", "linux", "redis", "kafka", "terraform", "spark", "opencv",
        "graphql", "microservices", "ci/cd", "mlops", "airflow", "data engineering"
    ]

    for skill in found:
        skill_lower = skill.lower()
        if any(skill_lower in kw or kw in skill_lower for kw in strong_required_keywords):
            required.append(skill)
        elif any(skill_lower in kw or kw in skill_lower for kw in preferred_keywords):
            preferred.append(skill)

    # Include all found skills in required if none were detected
    if not required and not preferred:
        required = found[:10]

    return {
        "required": sorted(set(required), key=lambda x: x.lower()),
        "preferred": sorted(set(preferred), key=lambda x: x.lower()),
        "tools": []
    }


def extract_job_skills(job_description: str, api_key: str = None, model: str = None) -> Dict[str, List[str]]:
    """Extract required and preferred skills from a job description.

    First tries OpenRouter API when credentials are available. Falls back to keyword-based parsing.
    """
    if api_key:
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
You are an expert recruiter and technical skills extractor.

Analyze the following job description and return valid JSON only.

Return structure:
{{
  "required": ["top must-have skills"],
  "preferred": ["nice-to-have skills"],
  "tools": ["tools, frameworks, platforms mentioned"]
}}

Job description:
{job_description[:4000]}
"""

            response = client.chat.completions.create(
                model=model or "nvidia/nemotron-3-ultra-550b-a55b",
                messages=[
                    {"role": "system", "content": "You extract technical skills from job descriptions and return valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            content = response.choices[0].message.content
            if content:
                parsed = json.loads(content)
                required = parsed.get("required", []) or []
                preferred = parsed.get("preferred", []) or []
                tools = parsed.get("tools", []) or []
                if required or preferred or tools:
                    return {
                        "required": [normalize_skill(x) for x in required],
                        "preferred": [normalize_skill(x) for x in preferred],
                        "tools": [normalize_skill(x) for x in tools],
                    }
        except Exception:
            pass

    return get_job_skill_fallback(job_description)


def compare_skills(resume_skills: List[str], job_required_skills: List[str], job_preferred_skills: List[str] = None) -> Dict[str, Any]:
    """Compare candidate skills with job skills and generate a summary."""
    resume_set = {normalize_skill(skill).lower() for skill in resume_skills}
    required = [normalize_skill(skill) for skill in job_required_skills or []]
    preferred = [normalize_skill(skill) for skill in (job_preferred_skills or [])]

    matched = []
    missing_critical = []
    missing_preferred = []

    for skill in required:
        if skill.lower() in resume_set:
            matched.append(skill)
        else:
            missing_critical.append(skill)

    for skill in preferred:
        if skill.lower() in resume_set:
            matched.append(skill)
        else:
            missing_preferred.append(skill)

    matched = sorted(set(matched), key=lambda x: x.lower())
    missing_critical = sorted(set(missing_critical), key=lambda x: x.lower())
    missing_preferred = sorted(set(missing_preferred), key=lambda x: x.lower())

    total_critical = max(len(required), 1)
    score = round((len(matched) / total_critical) * 100, 1)

    if missing_critical:
        gap_summary = (
            f"Your resume covers {len(matched)} skill(s) from the job requirements. "
            f"Critical gaps: {', '.join(missing_critical[:5])}. "
            f"Preferred gaps: {', '.join(missing_preferred[:5]) if missing_preferred else 'none'}"
        )
    else:
        gap_summary = (
            f"Your resume is strong for this role. You match {len(matched)} required skill(s). "
            f"Preferred gaps: {', '.join(missing_preferred[:5]) if missing_preferred else 'none'}"
        )

    return {
        "matched": matched,
        "missing_critical": missing_critical,
        "missing_preferred": missing_preferred,
        "score": score,
        "gap_summary": gap_summary,
    }


def analyze_skill_gaps(resume_skills: List[str], job_description: str, api_key: str = None, model: str = None) -> Dict[str, Any]:
    """Get job-required skills and compare against resume skills."""
    extracted = extract_job_skills(job_description, api_key=api_key, model=model)
    required = extracted.get("required", [])
    preferred = extracted.get("preferred", [])

    comparison = compare_skills(resume_skills, required, preferred)

    return {
        "required_skills": required,
        "preferred_skills": preferred,
        "matched": comparison["matched"],
        "missing_critical": comparison["missing_critical"],
        "missing_preferred": comparison["missing_preferred"],
        "score": comparison["score"],
        "gap_summary": comparison["gap_summary"],
        "tools": extracted.get("tools", []),
    }
