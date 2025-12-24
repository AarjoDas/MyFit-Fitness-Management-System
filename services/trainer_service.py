from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import date, datetime
from typing import List, Dict, Any

from models.trainer import Trainer
from models.member import Member
from models.personal_training_session import PersonalTrainingSession, SessionStatus
from models.group_class import GroupClass
from models.class_enrollment import ClassEnrollment

class TrainerService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_trainer_schedule(self, trainer_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        classes = self.db.query(GroupClass).filter(
            GroupClass.trainer_id == trainer_id,
            GroupClass.scheduled_date >= start_date,
            GroupClass.scheduled_date <= end_date
        ).all()

        pt_sessions = self.db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.trainer_id == trainer_id,
            PersonalTrainingSession.scheduled_date >= start_date,
            PersonalTrainingSession.scheduled_date <= end_date,
        ).all()

        schedule = []
        
        for c in classes:
            schedule.append({
                "type": "Group Class",
                "id": c.class_id,
                "name": c.class_name,
                "date": c.scheduled_date,
                "start_time": c.start_time,
                "end_time": c.end_time,
                "room": c.room.room_name if c.room else "Unassigned",
                "capacity_status": f"{c.current_enrollment}/{c.capacity}"
            })

        for s in pt_sessions:
            member_name = f"{s.member.first_name} {s.member.last_name}" if s.member else "Unknown"
            schedule.append({
                "type": "PT Session",
                "id": s.session_id,
                "name": f"Session with {member_name}",
                "date": s.scheduled_date,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "room": s.room.room_name if s.room else "Unassigned",
                "status": s.status.value
            })

        schedule.sort(key=lambda x: (x['date'], x['start_time']))
        return schedule

    def search_members(self, query_name: str) -> List[Member]:
        search_term = f"%{query_name}%"
        members = self.db.query(Member).filter(
            or_(
                Member.first_name.ilike(search_term),
                Member.last_name.ilike(search_term)
            )
        ).all()
        return members

    def view_member_profile(self, member_id: int) -> Dict[str, Any]:
        member = self.db.query(Member).get(member_id)
        if not member:
            raise ValueError("Member not found.")

        recent_classes = self.db.query(ClassEnrollment).filter(
            ClassEnrollment.member_id == member_id
        ).limit(5).all()

        return {
            "full_name": f"{member.first_name} {member.last_name}",
            "email": member.email,
            "gender": member.gender.value if member.gender else "N/A",
            "recent_activity": [
                f"Class: {e.group_class.class_name} ({e.attendance_status.value})" 
                for e in recent_classes if e.group_class
            ]
        }

    def update_session_notes(self, session_id: int, notes: str):
        session = self.db.query(PersonalTrainingSession).get(session_id)
        if not session:
            raise ValueError("Session not found.")
        
        session.notes = notes
        self.db.commit()
        return session

    def update_session_status(self, session_id: int, new_status: str):
        """
        Updates the status of a PT session (e.g. to 'Completed' or 'No Show').
        """
        session = self.db.query(PersonalTrainingSession).get(session_id)
        if not session:
            raise ValueError("Session not found.")
        
        try:
            # Convert string input to Enum
            status_enum = SessionStatus(new_status)
        except ValueError:
            valid_options = [s.value for s in SessionStatus]
            raise ValueError(f"Invalid status '{new_status}'. Valid options: {valid_options}")

        session.status = status_enum
        self.db.commit()
        return session
    
    def get_all_trainers(self):
        return self.db.query(Trainer).all()

    def get_all_members(self):
        return self.db.query(Member).all()