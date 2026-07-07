from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class CreateStudySubjectRequest(BaseModel):
    name:str
    user_id:UUID
    class Config:
        from_attributes = True
class StudySubjectResponse(BaseModel):
    user_id:UUID 
    name:str
    id:UUID
    class Config:
        from_attributes = True