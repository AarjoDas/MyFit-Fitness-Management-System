from sqlalchemy import Column, Integer, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from database.connection import Base
import enum

class AttendanceStatus(enum.Enum):
    REGISTERED = "Registered"
    ATTENDED = "Attended"
    ABSENT = "Absent"
    CANCELLED = "Cancelled"

class ClassEnrollment(Base):
    __tablename__ = 'class_enrollments'
    
    # Attributes
    enrollment_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('group_classes.class_id'), nullable=False)
    member_id = Column(Integer, ForeignKey('members.member_id'), nullable=False)
    enrollment_date = Column(Date, nullable=False)
    attendance_status = Column(Enum(AttendanceStatus), default=AttendanceStatus.REGISTERED)
    
    # Relationships
    group_class = relationship("GroupClass", back_populates="enrollments")
    member = relationship("Member", back_populates="class_enrollments")
    
    def __repr__(self):
        return f"<ClassEnrollment(class={self.class_id}, member={self.member_id}, status={self.attendance_status.value})>"