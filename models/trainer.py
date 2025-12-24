from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database.connection import Base

class Trainer(Base):
    __tablename__ = "trainers"

    # Attributes
    trainer_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialization = Column(String(200))
    hire_date = Column(Date)

    # Relationships
    pt_sessions = relationship("PersonalTrainingSession", back_populates="trainer")
    group_classes = relationship("GroupClass", back_populates="trainer")

    def __repr__(self):
        return f"<Trainer(id={self.trainer_id}, name={self.first_name} {self.last_name})>"