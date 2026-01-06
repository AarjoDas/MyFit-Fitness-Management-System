from sqlalchemy import Column, Integer, String, Date
from database.connection import Base

class AdminStaff(Base):
    __tablename__ = 'admin'

    # attributes
    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(100))
    phone = Column(String(20))
    hire_date = Column(Date)
    
    def __repr__(self):
        return f"<Admin(id={self.admin_id}, name={self.first_name} {self.last_name}, role={self.role})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"