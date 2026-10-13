# 🎯 HireReady AI — Resume Intelligence & Interview Preparation

**An AI-powered career preparation platform that helps job seekers analyze their resumes, identify skill gaps, build learning roadmaps, and practice company-focused interviews.**

🌐 **Live Demo:** [Try HireReady AI](https://hireready-ai-rwqs2dxzg2rakzno7omrcl.streamlit.app/)  
💻 **Source Code:** [GitHub Repository](https://github.com/MKPATHY154/hireready-ai)

---

## 📌 Overview

HireReady AI is a Python-based web application built with Streamlit to support job seekers throughout their interview preparation journey.

The platform brings resume analysis, job-description alignment, skill-gap identification, learning roadmaps, company interview research, AI-generated interview questions, and answer evaluation into one interface.

It combines Python-based processing with AI services and public web research to help users understand what to improve and practice answering interview questions.

## ✨ Features

### 📄 1. Resume & Job Description Analysis
- Upload a resume for processing.
- Extract resume text from PDF documents.
- Identify skills and information relevant to a target role.
- Use resume and job-description information to support career preparation.

### 🧩 2. Skill-Gap Analysis
- Compare candidate skills with job-related requirements.
- Identify skills that may need further development.
- Help candidates focus their preparation on relevant topics.

### 🗺️ 3. Personalized Learning Roadmap
- Generate a learning roadmap to guide skill improvement.
- Organize preparation around the identified learning needs.
- Support structured, goal-oriented interview preparation.

### 📊 4. Progress Tracking
- Access the application's progress-tracking section.
- Review preparation progress using the functionality available in the application.

### 🔎 5. Company Interview Research
- Select a company and interview round.
- Search public web resources using the Tavily API.
- Display research results with titles, summaries, and source links.
- Use the research as context for interview preparation.

### 🤖 6. AI-Generated Interview Questions
- Generate interview questions using an OpenRouter-compatible language model.
- Use the selected company, interview round, role focus, and retrieved research as context.
- Support preparation for technical, coding, system-design, HR, and other selected interview rounds.

AI-generated questions are preparation suggestions, not guarantees that a company will ask those exact questions.

### 🎤 7. Interactive Mock Interview
- Present interview questions for practice.
- Allow candidates to enter their answers.
- Evaluate submitted answers using an AI model.
- Provide a score, strengths, improvement suggestions, and a sample answer.
- Support reviewing feedback while progressing through the interview.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and processing |
| Streamlit | Interactive web application |
| OpenAI Python SDK | Client interface for model requests |
| OpenRouter | Access to the configured language model |
| Tavily API | Public web search for company interview research |
| PyMuPDF | PDF text extraction |
| python-dotenv | Local environment-variable loading |
| SQLite | Local application database functionality |
| Git and GitHub | Version control and source-code hosting |
| Streamlit Community Cloud | Application deployment |

The exact model used for AI generation is configurable through the `OPENROUTER_MODEL` environment variable.

## 🏗️ System Architecture

```text
                 ┌──────────────────────┐
                 │       User           │
                 │ Resume / Job Details │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Streamlit UI       │
                 │       app.py         │
                 └──────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │ Resume and │ │ Skill Gap  │ │ Learning   │
      │ JD Analysis│ │ Analysis   │ │ Roadmap    │
      └────────────┘ └────────────┘ └────────────┘

                 Interview Preparation
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
      ┌────────────────┐          ┌────────────────┐
      │ Tavily Research│          │ OpenRouter AI  │
      │ Public Sources │          │ Question and   │
      └───────┬────────┘          │ Answer Feedback│
              │                   └───────┬────────┘
              └────────────┬──────────────┘
                           ▼
                 ┌──────────────────────┐
                 │ Interview Practice   │
                 │ Scores and Feedback  │
                 └──────────────────────┘
```

*This diagram represents the application's main functional flow. It is a conceptual overview rather than a complete deployment diagram.*

## 📁 Project Structure

```text
hireready-ai/
│
├── app.py
├── interview_generator.py
├── ai_question_generator.py
├── answer_evaluator.py
├── company_research.py
├── resume_parser.py
├── skill_analyzer.py
├── roadmap_generator.py
├── database.py
│
├── tests/
│   ├── test_interview_generator.py
│   └── test_roadmap_generator.py
│
├── test_company_research.py
├── test_tavily.py
├── requirements.txt
├── PROJECT_DOCUMENTATION.md
├── FEATURE_INTEGRATION_PLAN.md
├── .gitignore
└── README.md
```

**Note:** `.env`, the local virtual environment, Python cache files, and the local SQLite database are intentionally excluded from version control. The structure above lists the principal project files; additional files may be present.

## ⚙️ Run Locally

### Prerequisites

- Python installed on your system.
- Git installed.
- An OpenRouter API key for AI-powered features.
- A Tavily API key for company interview research.

### 1. Clone the repository

```bash
git clone https://github.com/MKPATHY154/hireready-ai.git
cd hireready-ai
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a file named `.env` in the project root, alongside `app.py`.

Add your own API keys:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b
TAVILY_API_KEY=your_tavily_api_key
```

Replace the example values with your own credentials.

**Never commit `.env` to GitHub or expose your API keys in screenshots, logs, or public documentation.**

### 5. Start the application

```bash
streamlit run app.py
```

Open the local URL printed in your terminal, typically:

`http://localhost:8501`

## 🔐 API Configuration

### OpenRouter
Used to access the configured language model for AI-generated interview questions and answer evaluation.

Website: https://openrouter.ai/

### Tavily
Used to retrieve public web research relevant to company interview preparation.

Website: https://tavily.com/

### Local development and deployment

- Local development uses environment variables loaded from `.env`.
- Streamlit Community Cloud should use its **Secrets** settings for API credentials.
- Keep the same variable names in both environments.
- API usage, rate limits, and costs depend on the selected providers and their account plans.

## ☁️ Deployment

The application is deployed using Streamlit Community Cloud.

**Live application:**  
https://hireready-ai-rwqs2dxzg2rakzno7omrcl.streamlit.app/

To deploy your own copy:

1. Fork or clone the GitHub repository.
2. Open https://share.streamlit.io/.
3. Connect your GitHub account.
4. Select the repository and the `main` branch.
5. Set `app.py` as the main file.
6. Configure the required API keys under the app's Secrets settings.
7. Deploy the application and review its logs if any errors occur.

Ensure that `requirements.txt` includes the external packages required by the application.

## 🧪 Testing

The repository includes test files for interview generation, roadmap generation, company research, and Tavily integration.

Run the test suite with:

```bash
python -m pytest
```

Some integration tests may require valid API credentials and network access. Configure the required environment variables before running tests that call external services.

## 🔒 Security and Privacy

- API keys must be stored in environment variables or deployment secrets.
- Do not commit `.env`, private credentials, or generated local database files.
- Treat uploaded resumes and job descriptions as potentially sensitive information.
- Review third-party API privacy policies before submitting personal or confidential data.
- AI-generated questions, scores, and feedback can be inaccurate and should be reviewed critically.

## ⚠️ Limitations

- The quality of generated questions and feedback depends on the selected language model and the information provided.
- Public web research may contain incomplete, outdated, or unverified information.
- Search results do not establish that a question was actually asked in a specific interview.
- AI scores and sample answers are guidance for practice, not authoritative measures of employability.
- External API availability, usage limits, and costs may affect AI-powered functionality.
- Local database persistence and hosted deployment behavior depend on the configured runtime and storage environment.

## 🚀 Future Improvements

Potential areas for future development include:

- More detailed interview performance summaries.
- Improved question organization and filtering.
- Expanded test coverage for application modules.
- Additional documentation and user guidance.
- Further improvements to progress tracking and learning recommendations.

These are possible enhancements, not claims about features already implemented.

## 👨‍💻 Author

**Manoj Kumar Pathy**

GitHub: https://github.com/MKPATHY154

## 📄 License

No license is specified in this README. Add a license only after choosing the terms under which you want others to use, modify, and distribute the project.

---

If you find the project useful, consider starring the repository or sharing feedback through GitHub Issues.