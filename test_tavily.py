
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    print("Tavily API key not found in .env")
else:
    try:
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query="Amazon software engineer Python interview questions",
            max_results=3
        )

        results = response.get("results", [])

        if results:
            print("Tavily connection successful!")

            for index, result in enumerate(results, start=1):
                print("\nResult", index)
                print("Title:", result.get("title", ""))
                print("URL:", result.get("url", ""))
                print("Snippet:", result.get("content", "")[:200])
        else:
            print("Connected, but no results were returned.")

    except Exception as error:
        print("Search failed:", error)
