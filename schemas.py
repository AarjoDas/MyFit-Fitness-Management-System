from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional, List

# Member Schema
class MemberBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: date
    gender: str

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    member_id: int
    registration_date: date
    class Config:
        from_attributes = True

# PT Session Schemas
class PTSessionCreate(BaseModel):
    member_id: int
    trainer_id: int
    room_id: int
    scheduled_date: date
    start_time: time
    end_time: time
    notes: Optional[str] = None