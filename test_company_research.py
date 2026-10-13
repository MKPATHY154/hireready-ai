
from company_research import research_company_interviews

results = research_company_interviews(
    company="Amazon",
    role="Python Developer",
    interview_round="Technical Round"
)

if not results:
    print("No search results found.")
else:
    for index, result in enumerate(results, start=1):
        print("\nResult", index)
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Snippet:", result["snippet"][:250])
