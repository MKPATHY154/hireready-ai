
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_company_questions(
    company,
    role,
    interview_round,
    research_results
):
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3-ultra-550b-a55b"
    )

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing from .env"
        )

    if not research_results:
        raise ValueError(
            "No research results available. Run company research first."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    source_text = ""

    for index, result in enumerate(research_results, start=1):
        source_text += (
            "\nSource " + str(index) + "\n"
            + "Title: " + result.get("title", "") + "\n"
            + "URL: " + result.get("url", "") + "\n"
            + "Details: " + result.get("snippet", "") + "\n"
        )

    prompt = """
You are an interview preparation assistant.

Generate exactly 10 useful interview questions for the candidate.

Company: {company}
Role: {role}
Interview round: {interview_round}

Use the supplied web research as evidence. Do not claim that a
question was actually asked by the company unless the sources
directly support that claim.

For every question, provide:
1. Question number and question.
2. A short explanation of why it is relevant.
3. An evidence label:
   - Candidate-reported: supported by candidate experience sources.
   - Officially documented: supported by official company sources.
   - AI-predicted: a reasonable prediction, not verified as an actual question.
4. A source URL when a source supports the question. Otherwise,
   write "No direct supporting source".

Make the questions relevant to the selected role and round.
Do not invent source URLs.
Return readable, numbered text.

WEB RESEARCH:
{source_text}
""".format(
        company=company,
        role=role,
        interview_round=interview_round,
        source_text=source_text
    )

    response = client.chat.completions.create(
         model=model,
    messages=[
        {
            "role": "system",
            "content": (
                "You generate evidence-aware interview "
                "preparation questions."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.4,
    max_tokens=2500
)


    return response.choices[0].message.content
