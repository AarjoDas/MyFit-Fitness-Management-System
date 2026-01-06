from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship
from database.connection import Base
import enum

class GenderEnum(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class Member(Base):
    __tablename__ = 'members'

    # Attributes
    member_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum))
    registration_date = Column(Date, nullable=False)

    # Relationships
    pt_sessions = relationship("PersonalTrainingSession", back_populates="member")
    class_enrollments = relationship("ClassEnrollment", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(id={self.member_id}, name={self.first_name} {self.last_name})>"