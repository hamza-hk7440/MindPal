from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class CreateStudySubjectRequest(BaseModel):
    name:str
    created_at:datetime
    class Config:
        from_attributes = True
class StudySubjectResponse(BaseModel):
    id:UUID 
    name:str
    created_at:datetime
    class Config:
        from_attributes = True