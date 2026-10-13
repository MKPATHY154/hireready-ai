from interview_generator import generate_interview_questions
from company_research import research_company_interviews
from ai_question_generator import generate_company_questions
from answer_evaluator import evaluate_answer
import json
import os
import re 
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from resume_parser import parse_resume, extract_skills
from database import (
    init_db,
    create_session,
    save_skill_gap,
    get_latest_session,
    save_roadmap,
    get_roadmap_by_session,
    get_roadmap_tasks,
    update_task_completion,
    init_progress,
    get_progress,
    get_task_completion_stats,
    update_progress_on_task_complete,
)
from skill_analyzer import analyze_skill_gaps
from roadmap_generator import generate_roadmap
from interview_generator import generate_interview_questions

load_dotenv()

st.set_page_config(
    page_title="HireReady AI",
    page_icon="🎯"
)

st.title("HireReady AI")
st.subheader("AI-Powered Career Readiness Platform")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

# Initialize database for new features
init_db()

# Persistent session state
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "gap_result" not in st.session_state:
    st.session_state.gap_result = None
if "roadmap_result" not in st.session_state:
    st.session_state.roadmap_result = None
if "roadmap_id" not in st.session_state:
    st.session_state.roadmap_id = None
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []
if "interview_role" not in st.session_state:
    st.session_state.interview_role = "balanced"
if "interview_style" not in st.session_state:
    st.session_state.interview_style = "general"


# Tab-based navigation for future modules
resume_tab, gap_tab, roadmap_tab, progress_tab, interview_tab = st.tabs([
    "📄 Resume & JD",
    "🔍 Skill Gap",
    "🗺️ Roadmap",
    "📊 Progress",
    "🎤 Mock Interview"
])


with resume_tab:
    st.header("1. Upload Resume")
    resume_file = st.file_uploader(
        "Upload your resume PDF",
        type=["pdf"]
    )

    if resume_file is not None:
        try:
            resume_text, resume_skills = parse_resume(resume_file)
            if resume_text.strip():
                st.session_state.resume_text = resume_text
                st.session_state.resume_skills = resume_skills
                st.success("Resume uploaded successfully!")
                st.write(
                    "Detected skills:",
                    ", ".join(resume_skills) if resume_skills else "No listed skills found."
                )
            else:
                st.warning("No selectable text found in this PDF.")
        except Exception as error:
            st.error("Unable to read PDF: " + str(error))

    st.divider()
    st.header("2. Enter Job Description")
    job_description = st.text_area(
        "Paste the job description",
        height=180,
        value=st.session_state.job_description,
    )
    st.session_state.job_description = job_description

    if st.button("Save Session Context", type="secondary"):
        if st.session_state.resume_text.strip() and st.session_state.job_description.strip():
            session_id = create_session(
                resume_text=st.session_state.resume_text,
                resume_skills=st.session_state.resume_skills,
                job_description=st.session_state.job_description,
                job_required_skills=[],
                job_preferred_skills=[]
            )
            st.session_state.session_id = session_id
            st.success(f"Session saved successfully! Session ID: {session_id}")
        else:
            st.warning("Please upload a resume and enter a job description before saving.")


with gap_tab:
    st.header("Skill-Gap Analysis")
    if not st.session_state.resume_text.strip() or not st.session_state.job_description.strip():
        st.info("Upload a resume and add a job description in the Resume tab first.")
    else:
        if st.button("Analyze Skill Gaps", type="primary"):
            try:
                result = analyze_skill_gaps(
                    st.session_state.resume_skills,
                    st.session_state.job_description,
                    api_key=OPENROUTER_API_KEY,
                    model=OPENROUTER_MODEL,
                )
                st.session_state.gap_result = result

                if st.session_state.session_id is not None:
                    save_skill_gap(
                        st.session_state.session_id,
                        result.get("matched", []),
                        result.get("missing_critical", []),
                        result.get("missing_preferred", []),
                        result.get("gap_summary", "")
                    )

                st.success("Skill gap analysis complete.")
            except Exception as error:
                st.error(f"Skill gap analysis failed: {error}")

        gap_result = st.session_state.gap_result
        if gap_result:
            st.subheader("Overall Match Score")
            score = gap_result.get("score", 0)
            st.metric("Role Match Score", f"{score}%")
            st.progress(min(100, max(0, int(score))))

            st.write(gap_result.get("gap_summary", ""))

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Matched Skills")
                skills = gap_result.get("matched", [])
                if skills:
                    st.write(", ".join(skills))
                else:
                    st.info("No direct skill matches found yet.")

            with col2:
                st.markdown("### Missing Critical Skills")
                missing = gap_result.get("missing_critical", [])
                if missing:
                    st.write(", ".join(missing))
                else:
                    st.success("No critical skill gaps found.")

            st.markdown("### Missing Preferred Skills")
            preferred = gap_result.get("missing_preferred", [])
            if preferred:
                st.write(", ".join(preferred))
            else:
                st.success("No preferred skill gaps found.")

            st.markdown("### Tools / Platforms Mentioned")
            tools = gap_result.get("tools", [])
            if tools:
                st.write(", ".join(tools))
            else:
                st.info("No additional tools detected from the job description.")

        else:
            st.write("Resume skills:", ", ".join(st.session_state.resume_skills) if st.session_state.resume_skills else "None")
            st.write("Job description length:", len(st.session_state.job_description))


with roadmap_tab:
    st.header("Personalized Learning Roadmap")
    if not st.session_state.resume_text.strip() or not st.session_state.job_description.strip():
        st.info("Complete the resume and job description first.")
    else:
        if st.button("Generate Roadmap", type="primary"):
            if st.session_state.session_id is None:
                session_id = create_session(
                    resume_text=st.session_state.resume_text,
                    resume_skills=st.session_state.resume_skills,
                    job_description=st.session_state.job_description,
                    job_required_skills=[],
                    job_preferred_skills=[],
                )
                st.session_state.session_id = session_id

            gap_result = st.session_state.gap_result
            if gap_result is None:
                gap_result = analyze_skill_gaps(
                    st.session_state.resume_skills,
                    st.session_state.job_description,
                    api_key=OPENROUTER_API_KEY,
                    model=OPENROUTER_MODEL,
                )
                st.session_state.gap_result = gap_result

            missing_skills = gap_result.get("missing_critical", []) + gap_result.get("missing_preferred", [])
            roadmap = generate_roadmap(
                missing_skills,
                st.session_state.job_description,
                api_key=OPENROUTER_API_KEY,
                model=OPENROUTER_MODEL,
            )
            st.session_state.roadmap_result = roadmap

            roadmap_id = save_roadmap(
                st.session_state.session_id,
                roadmap,
                total_weeks=len(roadmap.get("weeks", [])),
                estimated_hours_per_week=roadmap.get("hours_per_week", 8),
            )
            st.session_state.roadmap_id = roadmap_id
            init_progress(st.session_state.session_id, roadmap_id)
            st.success("Roadmap generated and saved successfully.")

        roadmap_data = st.session_state.roadmap_result
        if st.session_state.session_id is not None and roadmap_data is None:
            saved_roadmap = get_roadmap_by_session(st.session_state.session_id)
            if saved_roadmap:
                roadmap_data = json.loads(saved_roadmap["roadmap_data"])
                st.session_state.roadmap_result = roadmap_data
                st.session_state.roadmap_id = saved_roadmap["id"]

        if roadmap_data:
            st.subheader(roadmap_data.get("title", "Roadmap"))
            st.write(roadmap_data.get("summary", ""))

            for week in roadmap_data.get("weeks", []):
                with st.expander(f"Week {week.get('week', 1)} - {', '.join(week.get('skills', []))}", expanded=False):
                    st.markdown("### Focus skills")
                    st.write(", ".join(week.get("skills", [])))
                    st.markdown("### Tasks")
                    for task in week.get("tasks", []):
                        st.write("- " + task)
                    if week.get("resources"):
                        st.markdown("### Resources")
                        for resource in week.get("resources", []):
                            st.markdown(f"- [{resource.get('title', 'Resource')}]({resource.get('url', '#')})")
        else:
            st.info("No roadmap generated yet. Click the button to build your learning plan.")


with progress_tab:
    st.header("Progress Dashboard")
    if st.session_state.session_id is None:
        st.info("No saved session yet. Save a session in the Resume tab to start tracking progress.")
    else:
        roadmap_id = st.session_state.roadmap_id
        if roadmap_id is None:
            saved_roadmap = get_roadmap_by_session(st.session_state.session_id)
            if saved_roadmap:
                roadmap_id = saved_roadmap["id"]
                st.session_state.roadmap_id = roadmap_id

        if roadmap_id is None:
            st.info("Generate a roadmap first to start tracking progress.")
        else:
            tasks = get_roadmap_tasks(roadmap_id)
            stats = get_task_completion_stats(roadmap_id)
            completed = stats.get("completed", 0)
            total = stats.get("total", 0)
            percent = (completed / total * 100) if total else 0

            st.success(f"Current session: {st.session_state.session_id}")
            st.metric("Completion", f"{completed}/{total}")
            st.progress(int(percent))

            for task in tasks:
                task_id = task["id"]
                task_text = task["task_description"]
                is_completed = bool(task["is_completed"])
                checked = st.checkbox(
                    f"Week {task['week_number']} • {task_text}",
                    value=is_completed,
                    key=f"progress_task_{task_id}",
                )
                if checked != is_completed:
                    update_task_completion(task_id, checked)
                    update_progress_on_task_complete(st.session_state.session_id, roadmap_id, task["week_number"])
                    st.rerun()

            progress = get_progress(st.session_state.session_id)
            if progress:
                st.caption(
                    f"Current week: {progress.get('current_week', 1)} | "
                    f"Streak: {progress.get('streak_days', 0)} days"
                )


with interview_tab:
    st.header("AI Mock Interview")
    st.caption("Question patterns inspired by common technical, behavioral, and company interview loops.")
    
    st.subheader("Company Interview Research")

    company_name = st.selectbox(
        "Select Company",
        [
            "Amazon",
            "Google",
            "Microsoft",
            "Meta",
            "Infosys",
            "TCS",
            "Accenture",
            "Other"
        ],
        key="research_company"
    )

    if company_name == "Other":
        company_name = st.text_input(
            "Enter Company Name",
            key="custom_research_company"
        )

    interview_round = st.selectbox(
        "Select Interview Round",
        [
            "Online Assessment",
            "Technical Round",
            "Coding Round",
            "System Design Round",
            "HR Round",
            "Managerial Round"
        ],
        key="research_interview_round"
    )

    if st.button("Research Company Interviews"):
        if not company_name.strip():
            st.warning("Please enter a company name.")
        else:
            try:
                with st.spinner("Searching public interview resources..."):
                    results = research_company_interviews(
                        company=company_name,
                        role=st.session_state.interview_role,
                        interview_round=interview_round
                    )

                st.session_state["company_research_results"] = results
                st.session_state["generated_company_questions"] = ""
                st.session_state["mock_answers"] = {}
                st.session_state["mock_feedback"] = {}
                st.session_state["mock_question_index"] = 0

                if results:
                    st.success(
                        "Found " + str(len(results)) + " search results."
                    )
                else:
                    st.info("No results found. Try another search.")

            except Exception as error:
                st.error("Research failed: " + str(error))

    for result in st.session_state.get(
        "company_research_results", []
    ):
        st.markdown("**" + result.get("title", "Untitled") + "**")
        st.write(result.get("snippet", ""))

        source_url = result.get("url", "")
        if source_url.startswith("https://"):
            st.markdown("[Open source](" + source_url + ")")

        st.divider()
        
    st.subheader("AI-Generated Interview Questions")

    if st.button("Generate Top 10 Questions"):
        research_results = st.session_state.get(
            "company_research_results", []
        )

        if not research_results:
            st.warning(
                "Please research a company before generating questions."
            )
        else:
            try:
                with st.spinner(
                    "Generating interview questions..."
                ):
                    questions = generate_company_questions(
                        company=company_name,
                        role=st.session_state.interview_role,
                        interview_round=interview_round,
                        research_results=research_results
                    )

                st.session_state["generated_company_questions"] = questions

            except Exception as error:
                st.error(
                    "Question generation failed: " + str(error)
                )

    generated_questions = st.session_state.get(
        "generated_company_questions", ""
    )

    if generated_questions:
        st.markdown(generated_questions)

    # Interactive Mock Interview Simulator
    st.divider()
    st.subheader("Interactive Mock Interview")

    generated_text = st.session_state.get(
        "generated_company_questions", ""
    )

    if generated_text:
        question_matches = re.findall(
            r"(?m)^\s*(?:\*\*)?(?:Question\s*)?(\d{1,2})[.)\:]\s*(.+?)(?=\n|$)",
            generated_text
        )

        interview_questions = [
            match[1].strip().strip("*")
            for match in question_matches
            if 1 <= int(match[0]) <= 10
        ]

        # Remove duplicate questions while preserving order.
        interview_questions = list(dict.fromkeys(interview_questions))

        if interview_questions:
            if "mock_answers" not in st.session_state:
                st.session_state.mock_answers = {}

            if "mock_feedback" not in st.session_state:
                st.session_state.mock_feedback = {}

            if "mock_question_index" not in st.session_state:
                st.session_state.mock_question_index = 0

            if st.button(
                "Start / Restart Mock Interview",
                key="start_mock_interview"
            ):
                st.session_state.mock_answers = {}
                st.session_state.mock_feedback = {}
                st.session_state.mock_question_index = 0
                st.rerun()

            index = st.session_state.mock_question_index
            total = len(interview_questions)

            st.progress((index + 1) / total)
            st.caption(
                "Question " + str(index + 1)
                + " of " + str(total)
            )

            question = interview_questions[index]
            st.markdown("### " + question)

            answer = st.text_area(
                "Your answer",
                value=st.session_state.mock_answers.get(index, ""),
                height=180,
                key="answer_box_" + str(index),
                placeholder="Type your answer here..."
            )

            if st.button(
                "Submit Answer for Evaluation",
                key="evaluate_" + str(index)
            ):
                if not answer.strip():
                    st.warning("Please enter your answer first.")
                else:
                    try:
                        with st.spinner("Evaluating your answer..."):
                            feedback = evaluate_answer(
                                question=question,
                                candidate_answer=answer,
                                company=company_name,
                                role=st.session_state.interview_role,
                                interview_round=interview_round
                            )

                        st.session_state.mock_answers[index] = answer
                        st.session_state.mock_feedback[index] = feedback

                    except Exception as error:
                        st.error("Evaluation failed: " + str(error))

            feedback = st.session_state.mock_feedback.get(index)

            if feedback:
                st.markdown("### AI Feedback")
                st.markdown(feedback)

                if index < total - 1:
                    if st.button(
                        "Next Question",
                        key="next_question_" + str(index)
                    ):
                        st.session_state.mock_question_index = index + 1
                        st.rerun()
                else:
                    st.success("You have completed all interview questions!")

                    st.markdown("### Interview Summary")
                    st.write(
                        "Questions evaluated: "
                        + str(len(st.session_state.mock_feedback))
                    )

                    st.markdown("### Review Your Answers")
                    for question_index, previous_feedback in (
                        st.session_state.mock_feedback.items()
                    ):
                        with st.expander(
                            "Question " + str(question_index + 1)
                        ):
                            st.markdown(
                                interview_questions[question_index]
                            )
                            st.markdown(previous_feedback)
        else:
            st.warning(
                "Could not identify numbered questions. "
                "Please generate the questions again."
            )
    else:
        st.info(
            "Generate the top 10 company interview questions first "
            "to start the interactive interview."
        )


    if not st.session_state.resume_text.strip():
        st.info("Upload a resume to generate interview questions.")
    elif not st.session_state.job_description.strip():
        st.info("Enter a job description before generating questions.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.interview_role = st.selectbox(
                "Interview focus",
                ["balanced", "backend", "data", "ml", "product", "fullstack"],
                index=["balanced", "backend", "data", "ml", "product", "fullstack"].index(st.session_state.interview_role) if st.session_state.interview_role in ["balanced", "backend", "data", "ml", "product", "fullstack"] else 0,
            )
        with col2:
            st.session_state.interview_style = st.selectbox(
                "Company style",
                ["general", "google", "amazon", "meta", "startup"],
                index=["general", "google", "amazon", "meta", "startup"].index(st.session_state.interview_style) if st.session_state.interview_style in ["general", "google", "amazon", "meta", "startup"] else 0,
            )

        if st.button("Generate AI Interview Questions", type="primary"):
            try:
                with st.spinner("Generating job-specific interview questions..."):
                    questions = generate_interview_questions(
                        st.session_state.resume_skills,
                        st.session_state.job_description,
                        api_key=OPENROUTER_API_KEY,
                        model=OPENROUTER_MODEL,
                        role_focus=st.session_state.interview_role,
                        company_style=st.session_state.interview_style,
                    )
                st.session_state.interview_questions = questions
                st.success("Interview questions generated successfully.")
            except Exception as error:
                st.error("AI request failed: " + str(error))
                st.info(
                    "Check your OpenRouter API key, internet connection, model availability and API quota."
                )

        if not st.session_state.interview_questions:
            st.session_state.interview_questions = generate_interview_questions(
                st.session_state.resume_skills,
                st.session_state.job_description,
                api_key=OPENROUTER_API_KEY,
                model=OPENROUTER_MODEL,
                role_focus=st.session_state.interview_role,
                company_style=st.session_state.interview_style,
            )

        if st.session_state.interview_questions:
            st.header("Mock Interview Questions")
            for index, question in enumerate(st.session_state.interview_questions, start=1):
                st.markdown(f"{index}. {question}")
                st.write("")
        else:
            st.warning("No questions generated yet.")
