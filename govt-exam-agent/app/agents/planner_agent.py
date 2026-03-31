from app.services.llm_service import LLMService
import re

class PlannerAgent:

    def __init__(self):
        self.llm = LLMService()

    def extract_duration(self, text: str):
        text = text.lower()

        match = re.search(r'(\d+)\s*month', text)
        if match:
            return int(match.group(1))

        match = re.search(r'(\d+)\s*week', text)
        if match:
            weeks = int(match.group(1))
            return max(1, weeks // 4)

        return 3  # default

    def create_study_plan(self, exam_input: str):

        duration = self.extract_duration(exam_input)

        prompt = f"""
You are a HIGHLY ACCURATE government exam preparation expert.

User request: "{exam_input}"

Duration: {duration} months

⚠️ STRICT RULES (VERY IMPORTANT):
- Do NOT assume wrong subjects
- Choose subjects ONLY relevant to the exam
- If exam is general (RRB, SSC, TNPSC, Bank):
  → Subjects = General Awareness, Quantitative Aptitude, Reasoning, English
- Include technical subjects ONLY if exam explicitly requires it

- Do NOT generate fake books or random names
- Use ONLY well-known books (NCERT, RS Aggarwal, Arihant, Lucent, etc.)

- Plan MUST be EXACTLY for {duration} months (NOT 6 months default)

OUTPUT FORMAT (STRICT):

1. Exam Overview
2. Subjects (accurate)
3. Month-wise Plan (ONLY {duration} months)
   - Week-wise breakdown
4. Time Allocation (realistic %)
5. Standard Books (real ones only)
6. Online Resources (relevant)
7. Strategy
8. Revision Plan
9. Mock Test Plan

Make it clean, structured, and readable.
"""

        response = self.llm.generate([
            {"role": "user", "content": prompt}
        ])

        return {
            "exam": exam_input,
            "duration": duration,
            "plan": response
        }