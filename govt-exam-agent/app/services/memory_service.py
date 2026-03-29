from app.db import SessionLocal
from app.models import ChatMemory

class MemoryService:

    def get(self, session_id):
        db = SessionLocal()
        data = db.query(ChatMemory).filter_by(session_id=session_id).all()
        db.close()

        return [{"role": d.role, "content": d.content} for d in data]

    def update(self, session_id, role, content):
        db = SessionLocal()

        msg = ChatMemory(
            session_id=session_id,
            role=role,
            content=content
        )

        db.add(msg)
        db.commit()
        db.close()