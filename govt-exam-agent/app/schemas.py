from pydantic import BaseModel, Field
from typing import List, Optional


class MCQOption(BaseModel):
    """Single MCQ option"""
    option_letter: str = Field(..., description="A, B, C, D")
    text: str = Field(..., description="Option text")


class MCQQuestion(BaseModel):
    """Single MCQ question with options and answer"""
    question_id: int = Field(..., description="Question number")
    question_text: str = Field(..., description="The question")
    options: List[MCQOption] = Field(..., description="4 options (A, B, C, D)")
    correct_answer: str = Field(..., description="Correct option letter (A/B/C/D)")
    explanation: str = Field(..., description="Explanation of correct answer")
    difficulty: str = Field(default="medium", description="easy/medium/hard")


class MCQResponse(BaseModel):
    """MCQ generation response"""
    topic: Optional[str] = Field(None, description="Topic of MCQs")
    questions: List[MCQQuestion] = Field(..., description="List of MCQ questions")
    total_questions: int = Field(..., description="Total number of questions")


class StudyResponse(BaseModel):
    type: str = Field(...)
    content: str = Field(...)
    follow_up: str = Field(...)

    class Config:
        extra = "forbid"