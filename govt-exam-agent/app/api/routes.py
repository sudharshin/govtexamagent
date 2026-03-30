from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import json
from app.services.tavily_service import TavilyService
from app.utils.text_processing import extract_questions,extract_pdf_links
from app.agents.study_agent import StudyAgent
from app.agents.mcq_agent import MCQAgent

router = APIRouter()

study_agent = StudyAgent()
mcq_agent = MCQAgent()
tavily_service = TavilyService()

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
@router.get("/pyqs")
def get_previous_questions(exam: str):
    search_results = tavily_service.search_exam_content(exam)

    pdfs = []
    web_questions = []
    seen_urls = set()

    for result in search_results.get("results", []):
        url = result.get("url")
        title = result.get("title")

        # ✅ Skip invalid or duplicate URLs
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        try:
            extracted = tavily_service.extract_from_url(url)

            if not extracted.get("results"):
                continue

            first_result = extracted["results"][0]

            # ✅ Handle both content types
            content = first_result.get("content") or first_result.get("raw_content")

            if not content:
                continue

            # ✅ Extract PDF links from content
            pdf_links = extract_pdf_links(content)
            for pdf in pdf_links:
                pdfs.append({
                    "title": title,
                    "url": pdf
                })

            # ✅ Extract questions
            questions = extract_questions(content)

            if not questions:
                continue

            web_questions.append({
                "title": title,
                "url": url,
                "questions": questions[:5]  # limit
            })

        except Exception as e:
            print("Error while processing URL:", url)
            print("Error:", e)

    return {
        "exam": exam,
        "pdfs": pdfs,
        "web_questions": web_questions
    }