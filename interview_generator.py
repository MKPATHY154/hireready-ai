"""Interview question generation tuned to the job description and real company-style patterns."""

import json
import re
from typing import List

from openai import OpenAI

from resume_parser import SKILLS


COMMON_PATTERNS = {
    "python": [
        "Walk me through a Python project you built and explain the architecture, trade-offs, and testing strategy.",
        "How would you design a REST API in Python to handle authentication, validation, and error handling at scale?",
        "Describe a performance issue you debugged in Python. How did you identify the bottleneck and fix it?",
    ],
    "backend": [
        "Tell me about a time you improved a backend service's reliability or response time. What was the root cause?",
        "How would you design a backend system to support 1M daily users with low latency and good observability?",
        "Describe a production incident you handled and how you communicated the fix to stakeholders.",
        "If an API became slow during peak traffic, how would you isolate the underlying cause and prioritize a fix?",
    ],
    "api": [
        "Explain how you would design a versioned REST API for a product with changing requirements.",
        "What are the key trade-offs between synchronous and asynchronous API designs in a production system?",
        "How do you secure an API against abuse, misuse, and accidental data exposure?",
        "When would you choose a synchronous API vs queue-based async processing for a critical workflow?",
    ],
    "database": [
        "How do you identify and fix slow SQL queries in a production application?",
        "When would you denormalize data versus normalize it? Walk me through your decision process.",
        "Describe a schema design challenge you handled and the trade-offs you considered.",
        "Tell me about a time your production data model caused a bug and how you fixed it without downtime.",
    ],
    "docker": [
        "Walk me through your Docker workflow from development to deployment, including image optimization and environment consistency.",
        "How do you debug a container that works locally but fails in production?",
        "What are the trade-offs between monolith and microservice deployment patterns in Dockerized systems?",
        "How would you reduce image size, improve caching, and keep deployments reproducible across environments?",
    ],
    "cloud": [
        "How would you deploy and monitor a service in AWS/Azure/GCP with minimal downtime?",
        "Describe a time you improved deployment reliability or rollback strategy in a cloud environment.",
        "What metrics would you monitor for service health and user impact?",
        "How would you design a zero-downtime deployment strategy for a customer-critical API?",
    ],
    "ml": [
        "Explain how you would evaluate a machine learning model before shipping it to production.",
        "What metrics would you use to decide whether a model is reliable enough for real users?",
        "Tell me about a time when the model underperformed in production and how you debugged it.",
        "How do you decide whether to ship a model improvement or keep the current system stable?",
    ],
    "leadership": [
        "Tell me about a time you had to influence a team without direct authority.",
        "Describe a project where you had to handle ambiguity and make progress with incomplete information.",
        "What is a time you disagreed with a stakeholder and how did you resolve it?",
        "Tell me about a project where you had to balance speed with quality under tight delivery constraints.",
    ],
    "data": [
        "Walk me through how you would design a data pipeline for a growing product and ensure data quality at each step.",
        "How do you decide between batch processing and streaming for a real-time analytics workflow?",
        "Describe a time you had to debug data drift, missing events, or pipeline failures in production.",
        "How would you validate the correctness of an ETL pipeline before moving it to production?",
    ],
    "fullstack": [
        "Tell me about a full-stack feature you built end-to-end. What trade-offs did you make between frontend speed and backend robustness?",
        "How do you balance product requirements, UX, and API contracts across frontend and backend teams?",
        "Describe a bug caused by mismatched API contracts and how you prevented it from happening again.",
    ],
    "product": [
        "How would you prioritize a feature request when business demand is high but engineering capacity is limited?",
        "Tell me about a decision you made where the product trade-off was unclear and how you gathered evidence.",
        "Describe a time you had to align technical decisions with user impact and business goals.",
    ],
    "general": [
        "Why do you want to work in this role, and what would success look like in the first 6 months?",
        "What are your strongest strengths and the biggest area you are still developing?",
        "Tell me about a time you had to learn a new technology quickly and how you approached it.",
        "Describe a challenge you solved where a quick fix would have been risky. What did you do instead?",
    ],
}

COMPANY_STYLE_PATTERNS = {
    "google": [
        "How would you structure the problem and communicate a design decision to a cross-functional team?",
        "Describe a time you made an engineering trade-off that improved maintainability and long-term quality.",
        "How do you balance speed with correctness when the system is under real user pressure?",
    ],
    "amazon": [
        "Tell me about a time you drove a project from ambiguity to delivery using strong prioritization.",
        "How do you make decisions when you have conflicting customer requirements and engineering constraints?",
        "Describe a situation where you had to improve a process or system that impacted many teams.",
    ],
    "meta": [
        "How would you improve the user experience of a product feature without breaking current performance expectations?",
        "Tell me about a time you partnered closely with product or design to ship something users actually value.",
        "How do you think about metrics and product health when launching a new feature?",
    ],
    "startup": [
        "How do you handle ambiguity and moving goals when requirements change quickly in a startup environment?",
        "Tell me about a time you had to build something fast without perfect data or a mature process.",
        "How do you prioritize between speed-to-market and technical debt when building a new product?",
    ],
    "general": [
        "Why do you want to work here, and what would you like to learn in your first few months?",
        "How do you handle changing priorities when multiple teams depend on your work?",
        "What would a strong first 90 days look like in this role?",
    ],
}


def normalize_question(raw: str) -> str:
    text = re.sub(r"\s+", " ", str(raw or "").strip())
    return text


def detect_job_role(job_description: str) -> str:
    text = (job_description or "").lower()
    if any(keyword in text for keyword in ["data engineer", "etl", "data pipeline", "warehouse", "spark"]):
        return "data"
    if any(keyword in text for keyword in ["full stack", "frontend", "frontend developer", "react", "javascript", "node"]):
        return "fullstack"
    if any(keyword in text for keyword in ["machine learning", "ml engineer", "ai engineer", "llm", "model"]):
        return "ml"
    if any(keyword in text for keyword in ["product manager", "pm", "product strategy", "roadmap"]):
        return "product"
    if any(keyword in text for keyword in ["backend", "api", "server", "microservices", "distributed systems"]) or "python" in text:
        return "backend"
    return "general"


def detect_company_style(job_description: str) -> str:
    text = (job_description or "").lower()
    for style in ["amazon", "google", "meta", "startup"]:
        if style in text:
            return style
    return "general"


def extract_job_topics(job_description: str) -> List[str]:
    text = (job_description or "").lower()
    found = []

    for skill in SKILLS:
        skill_lower = skill.lower()
        if skill_lower in text:
            found.append(skill_lower)

    keyword_map = {
        "python": "python",
        "backend": "backend",
        "api": "api",
        "sql": "database",
        "database": "database",
        "docker": "docker",
        "aws": "cloud",
        "azure": "cloud",
        "gcp": "cloud",
        "kubernetes": "cloud",
        "machine learning": "ml",
        "llm": "ml",
        "rag": "ml",
        "leadership": "leadership",
        "team": "leadership",
        "product": "product",
        "data pipeline": "data",
        "etl": "data",
        "spark": "data",
    }

    for keyword, label in keyword_map.items():
        if keyword in text and label not in found:
            found.append(label)

    if not found:
        found = [detect_job_role(job_description)]

    return found[:5]


def build_default_interview_questions(resume_skills: List[str], job_description: str, role_focus: str = None, company_style: str = "general") -> List[str]:
    topics = extract_job_topics(job_description)
    role = (role_focus or detect_job_role(job_description) or "general").lower()
    style = (company_style or "general").lower()
    questions = []

    if role in COMMON_PATTERNS:
        for q in COMMON_PATTERNS[role]:
            questions.append(q)

    for topic in topics:
        if topic not in {role, "general"}:
            for q in COMMON_PATTERNS.get(topic, COMMON_PATTERNS["general"]):
                questions.append(q)

    for q in COMPANY_STYLE_PATTERNS.get(style, COMPANY_STYLE_PATTERNS["general"]):
        questions.append(q)

    job_text = (job_description or "").lower()
    if "design" in job_text or "system" in job_text:
        questions.append("If you had to scale this system from 1,000 users to 1,000,000 users, what would you change first and why?")
    if "team" in job_text or "stakeholder" in job_text or "collaboration" in job_text:
        questions.append("Describe a time you had to coordinate across teams to ship a feature with incomplete requirements.")
    if "debug" in job_text or "performance" in job_text or "optimization" in job_text:
        questions.append("Tell me about a production issue you solved where the fix required measuring, isolating, and validating bottlenecks.")

    if not any("Tell me about" in q.lower() for q in questions):
        questions.append("Tell me about a time you had to learn something quickly, adapt your approach, and deliver results under pressure.")
    if not any("Why do you want" in q for q in questions):
        questions.append("Why do you want to work in this role, and what makes you a strong fit for this team and company?")

    unique = []
    seen = set()
    for q in questions:
        qn = normalize_question(q)
        if qn and qn.lower() not in seen:
            unique.append(qn)
            seen.add(qn.lower())

    return unique[:12]


def generate_interview_questions(resume_skills: List[str], job_description: str, api_key: str = None, model: str = None, role_focus: str = None, company_style: str = "general") -> List[str]:
    """Generate realistic interview questions tailored to the resume, role, and company-style patterns."""
    fallback = build_default_interview_questions(resume_skills, job_description, role_focus=role_focus, company_style=company_style)

    if not api_key or not job_description:
        return fallback

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://localhost",
                "X-OpenRouter-Title": "HireReady AI",
            },
        )

        role = (role_focus or detect_job_role(job_description) or "general").lower()
        style = (company_style or "general").lower()
        prompt = f"""
You are an expert technical recruiter. Generate realistic interview questions commonly used in {role}-focused and {style}-style technical interviews.

Requirements:
- Tailor to the candidate resume and the job description.
- Include technical, behavioral, and scenario-based questions.
- Use realistic questions commonly asked by companies like product, backend, data, ML, and platform teams.
- Return valid JSON only with a top-level array of strings.
- Use 8-12 questions, not more.

Candidate resume skills: {', '.join(resume_skills or [])}

Job description:
{job_description[:4000]}
"""

        response = client.chat.completions.create(
            model=model or "nvidia/nemotron-3-ultra-550b-a55b",
            messages=[
                {"role": "system", "content": "You generate realistic, role-specific interview questions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if not content:
            return fallback

        parsed = json.loads(content)
        if isinstance(parsed, list) and parsed:
            cleaned = [normalize_question(item) for item in parsed if normalize_question(item)]
            if cleaned:
                return cleaned[:12]
    except Exception:
        pass

    return fallback
