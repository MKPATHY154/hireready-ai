import unittest

from interview_generator import generate_interview_questions


class InterviewGeneratorTests(unittest.TestCase):
    def test_generate_interview_questions_are_job_specific_and_structured(self):
        questions = generate_interview_questions(
            resume_skills=["Python", "FastAPI", "SQL", "Docker"],
            job_description="We are hiring a Python backend engineer to design REST APIs, optimize database queries, and deploy services in Docker and AWS.",
        )

        self.assertGreater(len(questions), 6)
        self.assertTrue(any("FastAPI" in q or "REST" in q or "API" in q for q in questions))
        self.assertTrue(any("Docker" in q or "deploy" in q.lower() for q in questions))
        self.assertTrue(any("behavior" in q.lower() or "tell me about" in q.lower() for q in questions))

    def test_generate_interview_questions_for_data_role_and_google_style(self):
        questions = generate_interview_questions(
            resume_skills=["SQL", "Python", "Spark", "ETL"],
            job_description="Data Engineer role focused on data pipelines, ETL orchestration, data quality, and warehouse optimization.",
            role_focus="data",
            company_style="google",
        )

        self.assertGreater(len(questions), 5)
        self.assertTrue(any("pipeline" in q.lower() or "ETL" in q.upper() or "warehouse" in q.lower() for q in questions))
        self.assertTrue(any("trade-off" in q.lower() or "design" in q.lower() for q in questions))


if __name__ == "__main__":
    unittest.main()
