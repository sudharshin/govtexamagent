from app.services.llm_service import LLMService

class PlannerAgent:

    def __init__(self):
        self.llm = LLMService()

    def create_study_plan(self, exam_name: str):

        prompt = f"""
You are an expert government exam preparation mentor.

Create a COMPLETE STUDY PLAN for: {exam_name}

Include:
1. Exam Overview
2. Full Syllabus
3. Subject-wise topics
4. 3-month study plan (week-wise)
5. Time allocation per subject
6. Standard books (with authors)
6. Online resources (websites, YouTube channels)
8. Preparation strategy
9. Revision plan
10. Mock test strategy

Make it structured, detailed, and easy to follow.
"""

        messages = [
            {"role": "system", "content": "You are an expert exam planner."},
            {"role": "user", "content": prompt}
        ]

        result = self.llm.generate(messages)

        return {
            "exam": exam_name,
            "plan": result
        }