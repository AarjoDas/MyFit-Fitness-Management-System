from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class GroupClass(Base):
    __tablename__ = 'group_classes'
    
    # Attributes
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(200), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.trainer_id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False)
    
    # Relationships
    trainer = relationship("Trainer", back_populates="group_classes")
    room = relationship("Room", back_populates="group_classes")
    enrollments = relationship("ClassEnrollment", back_populates="group_class", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GroupClass(id={self.class_id}, name={self.class_name}, date={self.scheduled_date})>"
    
    @property
    def current_enrollment(self):
        """Get current number of active enrollments"""
        return len([e for e in self.enrollments if e.attendance_status.value in ["Registered", "Attended"]])
    
    @property
    def is_full(self):
        """Check if class is at capacity"""
        return self.current_enrollment >= self.capacity
    
    def get_active_enrollments(self):
        """Get all active enrollments (not cancelled)"""
        return [e for e in self.enrollments if e.attendance_status.value in ["Registered", "Attended"]]