import json
import re
from app.schemas import MCQQuestion, MCQOption, MCQResponse
from typing import List


class MCQService:
    """Service to parse and structure MCQ responses from LLM"""
    
    def parse_llm_response_to_mcq(self, llm_response: str) -> MCQResponse:
        """
        Parse raw LLM text response into structured MCQ format.
        The LLM should be prompted to return JSON-like format.
        """
        try:
            # Try to extract JSON from LLM response (if LLM returns JSON)
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                data = json.loads(json_match.group())
                return self._build_mcq_response(data)
            
            # Fallback: Parse structured text format
            return self._parse_text_format(llm_response)
        
        except Exception as e:
            print(f"Error parsing MCQ: {e}")
            # Return error MCQ response
            return self._create_error_mcq(llm_response)
    
    def _build_mcq_response(self, data: dict) -> MCQResponse:
        """Convert parsed JSON to MCQResponse"""
        questions = []
        
        for idx, q in enumerate(data.get("questions", []), 1):
            options = [
                MCQOption(option_letter=opt.get("letter"), text=opt.get("text"))
                for opt in q.get("options", [])
            ]
            
            question = MCQQuestion(
                question_id=idx,
                question_text=q.get("question", ""),
                options=options,
                correct_answer=q.get("correct_answer", ""),
                explanation=q.get("explanation", ""),
                difficulty=q.get("difficulty", "medium")
            )
            questions.append(question)
        
        return MCQResponse(
            topic=data.get("topic"),
            questions=questions,
            total_questions=len(questions)
        )
    
    def _parse_text_format(self, text: str) -> MCQResponse:
        """Parse natural text MCQ format"""
        questions = []
        
        # Split by question patterns
        q_pattern = r'(?:Q\d+|Question\s*\d+)[:\s]+(.*?)(?=Q\d+|Question\s*\d+|$)'
        q_matches = re.finditer(q_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for idx, match in enumerate(q_matches, 1):
            q_text = match.group(1).strip()
            
            # Extract options (A, B, C, D)
            options = self._extract_options(q_text)
            
            # Extract correct answer
            correct = self._extract_correct_answer(q_text)
            
            # Extract explanation
            explanation = self._extract_explanation(q_text)
            
            if options and len(options) >= 4:
                question = MCQQuestion(
                    question_id=idx,
                    question_text=q_text.split('\n')[0],  # First line is question
                    options=options[:4],
                    correct_answer=correct,
                    explanation=explanation,
                    difficulty="medium"
                )
                questions.append(question)
        
        return MCQResponse(
            questions=questions,
            total_questions=len(questions)
        )
    
    def _extract_options(self, text: str) -> List[MCQOption]:
        """Extract A, B, C, D options from text"""
        options = []
        
        # Match patterns like "A) ...", "A: ...", "A. ..."
        pattern = r'[A-D][\):\.]?\s*(.+?)(?=[A-D][\):\.]|\Z)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            letter = match.group(0)[0]
            option_text = match.group(1).strip()
            if option_text:
                options.append(MCQOption(option_letter=letter, text=option_text))
        
        return options
    
    def _extract_correct_answer(self, text: str) -> str:
        """Extract correct answer from text"""
        # Look for patterns like "Answer: A", "Correct: B", etc.
        pattern = r'(?:Answer|Correct|Right)[:\s]+([A-D])'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else "A"
    
    def _extract_explanation(self, text: str) -> str:
        """Extract explanation from text"""
        # Look for explanation patterns
        pattern = r'(?:Explanation|Why|Because)[:\s]+(.+?)(?=Answer|Correct|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else "See answer"
    
    def _create_error_mcq(self, raw_response: str) -> MCQResponse:
        """Create error MCQ when parsing fails"""
        question = MCQQuestion(
            question_id=1,
            question_text="Error in parsing",
            options=[
                MCQOption(option_letter="A", text="Unable to parse MCQ"),
                MCQOption(option_letter="B", text="Try again"),
                MCQOption(option_letter="C", text="Contact support"),
                MCQOption(option_letter="D", text="Refresh page"),
            ],
            correct_answer="B",
            explanation=f"Raw response:\n{raw_response}",
            difficulty="hard"
        )
        
        return MCQResponse(
            questions=[question],
            total_questions=1
        )
