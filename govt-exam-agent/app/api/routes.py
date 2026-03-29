from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import json

from app.agents.study_agent import StudyAgent
from app.agents.mcq_agent import MCQAgent

router = APIRouter()

study_agent = StudyAgent()
mcq_agent = MCQAgent()


class StudyRequest(BaseModel):
    session_id: str
    query: str
    has_document: bool = False


class MCQRequest(BaseModel):
    session_id: str
    topic: str = None
    num_questions: int = 3


@router.post("/study")
def study(req: StudyRequest):
    """
    General study endpoint for asking questions and getting explanations.
    For MCQ generation, use /mcq endpoint instead.
    - has_document: If True, prioritize document context; if False, use general knowledge
    """
    result = study_agent.handle(req.session_id, req.query, req.has_document)
    return result


@router.post("/mcq")
def generate_mcq(req: MCQRequest):
    """
    Dedicated endpoint for MCQ generation.
    
    If topic provided: Generate MCQs about that topic
    If no topic: Generate MCQs from uploaded document (if any)
    """
    result = mcq_agent.handle(
        req.session_id,
        topic=req.topic,
        num_questions=req.num_questions
    )
    
    return result


@router.post("/upload")
def upload(session_id: str, file: UploadFile = File(...)):
    """Upload PDF for RAG-based learning (shared by both agents)"""
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Load document into RAG (accessible by both agents)
    study_agent.rag.load_document(session_id, file_path)
    mcq_agent.rag.load_document(session_id, file_path)

    return {
        "success": True,
        "message": "File uploaded successfully",
        "file_name": file.filename
    }