from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connection import Base

class Room(Base):
    __tablename__ = 'rooms'
    
    # Attributes
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String(100), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    room_type = Column(String(50))
    
    # Relationships
    pt_sessions = relationship("PersonalTrainingSession", back_populates="room")
    group_classes = relationship("GroupClass", back_populates="room")
    
    def __repr__(self):
        return f"<Room(id={self.room_id}, name={self.room_name}, capacity={self.capacity})>"