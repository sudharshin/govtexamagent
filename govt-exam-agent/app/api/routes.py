from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.agents.study_agent import StudyAgent
from fastapi import UploadFile, File

router = APIRouter()

llm = LLMService()
memory = MemoryService()
agent = StudyAgent()

class StudyRequest(BaseModel):
    session_id: str
    query: str

@router.post("/study")
def study(req: StudyRequest):
    return agent.handle(req.session_id, req.query)
@router.post("/upload")
def upload(session_id: str, file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # ✅ IMPORTANT FIX
    agent.rag.load_document(session_id, file_path)

    return {"message": "Uploaded successfully"}