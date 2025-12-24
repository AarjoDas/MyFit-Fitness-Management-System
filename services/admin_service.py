from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date, time

from models.group_class import GroupClass
from models.room import Room
from models.trainer import Trainer
from models.member import Member 
from models.personal_training_session import PersonalTrainingSession, SessionStatus
from models.class_enrollment import ClassEnrollment, AttendanceStatus

# All admin functionality
class AdminService:
    def __init__(self, db_session: Session):
        self.db = db_session

    # Create new room
    def add_room(self, name: str, capacity: int, room_type: str = "General"):
        try:
            existing_room = self.db.query(Room).filter(Room.room_name == name).first()
            if existing_room:
                raise ValueError(f"Room with name '{name}' already exists.")

            new_room = Room(room_name=name, capacity=capacity, room_type=room_type)
            self.db.add(new_room)
            self.db.commit()
            return new_room
        except Exception as e:
            self.db.rollback()
            raise e

    # Create new trainer
    def add_trainer(self, first_name: str, last_name: str, email: str, specialization: str):
        try:
            new_trainer = Trainer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                specialization=specialization,
                hire_date=date.today()
            )
            self.db.add(new_trainer)
            self.db.commit()
            return new_trainer
        except Exception as e:
            self.db.rollback()
            raise e
     
    # Creating new group class
    def create_group_class(self, name: str, trainer_id: int, room_id: int, 
                           sched_date: date, start: time, end: time, capacity: int):
        try:
            room = self.db.query(Room).get(room_id)
            if not room:
                raise ValueError("Room not found.")
            
            if capacity > room.capacity:
                raise ValueError(f"Class capacity ({capacity}) cannot exceed room capacity ({room.capacity}).")

            if not self._is_room_available(room_id, sched_date, start, end):
                raise ValueError("The selected room is already booked for this time slot.")

            if not self._is_trainer_available(trainer_id, sched_date, start, end):
                raise ValueError("The trainer is already scheduled for a class or PT session at this time.")

            new_class = GroupClass(
                class_name=name,
                trainer_id=trainer_id,
                room_id=room_id,
                scheduled_date=sched_date,
                start_time=start,
                end_time=end,
                capacity=capacity
            )
            self.db.add(new_class)
            self.db.commit()
            return new_class
        except Exception as e:
            self.db.rollback()
            raise e

    #  Change time for a class
    def reschedule_class(self, class_id: int, new_date: date, new_start: time, new_end: time):
        try:
            group_class = self.db.query(GroupClass).get(class_id)
            if not group_class:
                raise ValueError("Class not found.")

            if not self._is_room_available(group_class.room_id, new_date, new_start, new_end, exclude_class_id=class_id):
                raise ValueError("Room is not available at the new time.")

            if not self._is_trainer_available(group_class.trainer_id, new_date, new_start, new_end, exclude_class_id=class_id):
                raise ValueError("Trainer is not available at the new time.")

            group_class.scheduled_date = new_date
            group_class.start_time = new_start
            group_class.end_time = new_end
            
            self.db.commit()
            return group_class
        except Exception as e:
            self.db.rollback()
            raise e

    # Remove class
    def cancel_class(self, class_id: int):
        try:
            group_class = self.db.query(GroupClass).get(class_id)
            if not group_class:
                raise ValueError("Class not found.")
            
            self.db.delete(group_class)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    # Check room availability
    def _is_room_available(self, room_id: int, check_date: date, start: time, end: time, exclude_class_id: int = None) -> bool:
        class_conflict_query = self.db.query(GroupClass).filter(
            GroupClass.room_id == room_id,
            GroupClass.scheduled_date == check_date,
            GroupClass.start_time < end,
            GroupClass.end_time > start
        )
        
        if exclude_class_id:
            class_conflict_query = class_conflict_query.filter(GroupClass.class_id != exclude_class_id)

        if class_conflict_query.first():
            return False

        pt_conflict = self.db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.room_id == room_id,
            PersonalTrainingSession.scheduled_date == check_date,
            PersonalTrainingSession.start_time < end,
            PersonalTrainingSession.end_time > start,
            PersonalTrainingSession.status != SessionStatus.CANCELLED 
        ).first()

        if pt_conflict:
            return False
        return True

    # Check trainer availability
    def _is_trainer_available(self, trainer_id: int, check_date: date, start: time, end: time, exclude_class_id: int = None) -> bool:
        class_conflict_query = self.db.query(GroupClass).filter(
            GroupClass.trainer_id == trainer_id,
            GroupClass.scheduled_date == check_date,
            GroupClass.start_time < end,
            GroupClass.end_time > start
        )

        if exclude_class_id:
            class_conflict_query = class_conflict_query.filter(GroupClass.class_id != exclude_class_id)
            
        if class_conflict_query.first():
            return False

        pt_conflict = self.db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.trainer_id == trainer_id,
            PersonalTrainingSession.scheduled_date == check_date,
            PersonalTrainingSession.start_time < end,
            PersonalTrainingSession.end_time > start,
            PersonalTrainingSession.status != SessionStatus.CANCELLED
        ).first()

        if pt_conflict:
            return False
        return True

    # Helpers
    def get_all_trainers(self):
        return self.db.query(Trainer).all()
    
    def get_all_rooms(self):
        return self.db.query(Room).all()
        
    def get_all_classes(self):
        return self.db.query(GroupClass).all()

    def get_all_members(self):
        """Added for Admin listing functionality"""
        return self.db.query(Member).all()