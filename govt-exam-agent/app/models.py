from sqlalchemy import Column, Integer, String, Text
from app.db import Base

class ChatMemory(Base):
    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)