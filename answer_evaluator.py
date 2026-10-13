
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def evaluate_answer(question, candidate_answer, company, role, interview_round):
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3-ultra-550b-a55b"
    )

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing from environment variables."
        )

    if not candidate_answer.strip():
        raise ValueError("Please enter your answer first.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    prompt = """
You are an experienced technical interviewer.
Evaluate the candidate's answer fairly and constructively.

Company: {company}
Role: {role}
Interview round: {interview_round}
Question: {question}
Candidate answer: {candidate_answer}

Return feedback using these headings:
SCORE (0-10)
STRENGTHS
IMPROVEMENTS
SAMPLE ANSWER

Be fair to different valid approaches. Do not invent facts about the candidate.
""".format(
        company=company,
        role=role,
        interview_round=interview_round,
        question=question,
        candidate_answer=candidate_answer
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Evaluate interview answers fairly and provide "
                    "useful, evidence-based feedback."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1200
    )

    return response.choices[0].message.content
