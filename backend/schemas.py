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

# Class Enrollment Schema
class ClassEnrollmentCreate(BaseModel):
    member_id: int
    class_id: int

# Trainer Schedule Schema
class TrainerScheduleRequest(BaseModel):
    trainer_id: int
    start_date: date
    end_date: date

# Trainer Session Update Schema
class SessionStatusUpdate(BaseModel):
    session_id: int
    status: str

class SessionNotesUpdate(BaseModel):
    session_id: int
    notes: str

# Admin Room Schema
class RoomCreate(BaseModel):
    name: str
    capacity: int
    room_type: Optional[str] = "General"

# Admin Trainer Schema
class TrainerCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    specialization: str

# Admin Group Class Schema
class GroupClassCreate(BaseModel):
    name: str
    trainer_id: int
    room_id: int
    scheduled_date: date
    start_time: time
    end_time: time
    capacity: int

class GroupClassReschedule(BaseModel):
    class_id: int
    new_date: date
    new_start: time
    new_end: time