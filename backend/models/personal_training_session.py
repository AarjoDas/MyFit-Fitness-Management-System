from sqlalchemy import Column, Integer, ForeignKey, Date, Time, String, Enum
from sqlalchemy.orm import relationship
from database.connection import Base
import enum

class SessionStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"

class PersonalTrainingSession(Base):
    __tablename__ = 'personal_training_sessions'
    
    # Attributes
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id'), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.trainer_id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    notes = Column(String(500))
    
    # Relationships
    member = relationship("Member", back_populates="pt_sessions")
    trainer = relationship("Trainer", back_populates="pt_sessions")
    room = relationship("Room", back_populates="pt_sessions")
    
    def __repr__(self):
        return f"<PTSession(id={self.session_id}, member={self.member_id}, trainer={self.trainer_id}, date={self.scheduled_date})>"