
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def research_company_interviews(company, role, interview_round):
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY is missing from .env")

    client = TavilyClient(api_key=api_key)

    query = (
        company
        + " "
        + role
        + " "
        + interview_round
        + " interview questions candidate experience"
    )

    response = client.search(
        query=query,
        max_results=10
    )

    research_results = []

    for result in response.get("results", []):
        research_results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "snippet": result.get("content", ""),
            "source_type": "Web search result"
        })

    return research_results
