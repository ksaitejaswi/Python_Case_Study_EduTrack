from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    completed_lessons_count: int
    status: str
    started_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True

class AchievementResponse(BaseModel):
    id: int
    title: str
    unlocked_at: datetime

    class Config:
        from_attributes = True        
