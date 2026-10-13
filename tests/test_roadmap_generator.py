import unittest

from roadmap_generator import generate_roadmap


class RoadmapGeneratorTests(unittest.TestCase):
    def test_generate_roadmap_builds_weekly_plan(self):
        result = generate_roadmap(
            ["FastAPI", "Docker", "REST API", "SQL"],
            "Build Python backend services with APIs and Docker deployment."
        )

        self.assertIn("weeks", result)
        self.assertGreaterEqual(len(result["weeks"]), 4)
        self.assertIn("FastAPI", result["weeks"][0]["skills"]) 
        self.assertTrue(any(task for week in result["weeks"] for task in week["tasks"]))


if __name__ == "__main__":
    unittest.main()
