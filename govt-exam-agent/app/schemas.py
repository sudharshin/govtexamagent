from pydantic import BaseModel, Field

class StudyResponse(BaseModel):
    type: str = Field(...)
    content: str = Field(...)
    follow_up: str = Field(...)

    class Config:
        extra = "forbid"