"""
Resume parsing module for HireReady AI.
Handles PDF text extraction and skill detection.
"""

import fitz
from typing import List, Tuple

# Predefined skill list - can be extended
SKILLS = [
    "Python", "Java", "C++", "SQL", "MySQL", "PostgreSQL", "MongoDB",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Artificial Intelligence", "Generative AI", "LLM", "RAG", "LangChain",
    "FastAPI", "Flask", "Django", "Streamlit", "Docker", "Kubernetes",
    "Git", "GitHub", "GitLab", "CI/CD", "Jenkins", "GitHub Actions",
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
    "OpenCV", "REST API", "GraphQL", "gRPC", "Microservices",
    "AWS", "Azure", "GCP", "Terraform", "Ansible", "Linux",
    "React", "Vue", "Angular", "TypeScript", "JavaScript", "HTML", "CSS",
    "Redis", "RabbitMQ", "Kafka", "Elasticsearch", "Prometheus", "Grafana",
]


def extract_resume_text(pdf_file) -> str:
    """
    Extract text from uploaded PDF file.
    
    Args:
        pdf_file: Streamlit uploaded file object
        
    Returns:
        Extracted text as string
    """
    document = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")
    text = ""
    for page in document:
        text += page.get_text() + "\n"
    document.close()
    return text


def extract_skills(text: str, skills_list: List[str] = None) -> List[str]:
    """
    Extract known skills from text.
    
    Args:
        text: Resume text to search
        skills_list: Optional custom skills list (defaults to SKILLS)
        
    Returns:
        List of found skills
    """
    if skills_list is None:
        skills_list = SKILLS
    
    found = []
    text_lower = text.lower()
    
    for skill in skills_list:
        if skill.lower() in text_lower:
            found.append(skill)
    
    return found


def parse_resume(pdf_file) -> Tuple[str, List[str]]:
    """
    Complete resume parsing: extract text and skills.
    
    Args:
        pdf_file: Streamlit uploaded file object
        
    Returns:
        Tuple of (resume_text, resume_skills)
    """
    resume_text = extract_resume_text(pdf_file)
    resume_skills = extract_skills(resume_text) if resume_text.strip() else []
    return resume_text, resume_skills


def get_skill_categories() -> dict:
    """
    Return skills organized by category for better UI display.
    """
    categories = {
        "Programming Languages": ["Python", "Java", "C++", "TypeScript", "JavaScript", "SQL"],
        "Databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch"],
        "AI/ML": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", 
                  "Artificial Intelligence", "Generative AI", "LLM", "RAG", "LangChain"],
        "Frameworks": ["FastAPI", "Flask", "Django", "Streamlit", "React", "Vue", "Angular",
                       "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "OpenCV"],
        "DevOps/Cloud": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible",
                         "Linux", "CI/CD", "Jenkins", "GitHub Actions", "Prometheus", "Grafana"],
        "Tools & Practices": ["Git", "GitHub", "GitLab", "REST API", "GraphQL", "gRPC",
                              "Microservices", "RabbitMQ", "Kafka"],
    }
    return categories


def get_skills_by_category(skills: List[str]) -> dict:
    """
    Group found skills by category.
    """
    categories = get_skill_categories()
    result = {}
    skills_lower = {s.lower(): s for s in skills}
    
    for category, cat_skills in categories.items():
        found = [skills_lower[s.lower()] for s in cat_skills if s.lower() in skills_lower]
        if found:
            result[category] = found
    
    return result