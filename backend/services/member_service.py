from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, time, datetime

from models.member import Member, GenderEnum
from models.group_class import GroupClass
from models.class_enrollment import ClassEnrollment, AttendanceStatus
from models.personal_training_session import PersonalTrainingSession, SessionStatus
from models.trainer import Trainer
from models.room import Room

class MemberService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def register_member(self, first_name: str, last_name: str, email: str, 
                        dob: date, gender: str) -> Member:
        try:
            existing = self.db.query(Member).filter(Member.email == email).first()
            if existing:
                raise ValueError(f"Member with email {email} already exists.")

            try:
                gender_enum = GenderEnum(gender)
            except ValueError:
                try:
                    gender_enum = GenderEnum(gender.capitalize())
                except ValueError:
                    raise ValueError(f"Invalid gender '{gender}'. Must be 'Male', 'Female', or 'Other'.")

            new_member = Member(
                first_name=first_name,
                last_name=last_name,
                email=email,
                date_of_birth=dob,
                gender=gender_enum,
                registration_date=date.today()
            )
            self.db.add(new_member)
            self.db.commit()
            return new_member
        except Exception as e:
            self.db.rollback()
            raise e

    def register_for_group_class(self, member_id: int, class_id: int) -> ClassEnrollment:
        try:
            member = self.db.query(Member).get(member_id)
            if not member: raise ValueError("Member not found.")

            group_class = self.db.query(GroupClass).get(class_id)
            if not group_class: raise ValueError("Class not found.")
            
            if group_class.is_full: raise ValueError("Class is fully booked.")

            existing = self.db.query(ClassEnrollment).filter(
                ClassEnrollment.member_id == member_id,
                ClassEnrollment.class_id == class_id,
                ClassEnrollment.attendance_status.in_([AttendanceStatus.REGISTERED, AttendanceStatus.ATTENDED])
            ).first()

            if existing: raise ValueError("Member is already registered.")

            new_enrollment = ClassEnrollment(
                member_id=member_id,
                class_id=class_id,
                enrollment_date=date.today(),
                attendance_status=AttendanceStatus.REGISTERED
            )
            self.db.add(new_enrollment)
            self.db.commit()
            return new_enrollment
        except Exception as e:
            self.db.rollback()
            raise e

    def schedule_pt_session(self, member_id: int, trainer_id: int, room_id: int, 
                            sched_date: date, start: time, end: time, notes: str = None) -> PersonalTrainingSession:
        try:
            if not self._is_trainer_available(trainer_id, sched_date, start, end):
                raise ValueError("Trainer is not available.")
            
            if not self._is_room_available(room_id, sched_date, start, end):
                raise ValueError("Room is not available.")

            new_session = PersonalTrainingSession(
                member_id=member_id,
                trainer_id=trainer_id,
                room_id=room_id,
                scheduled_date=sched_date,
                start_time=start,
                end_time=end,
                status=SessionStatus.SCHEDULED,
                notes=notes
            )
            self.db.add(new_session)
            self.db.commit()
            return new_session
        except Exception as e:
            self.db.rollback()
            raise e

    def get_member_dashboard_data(self, member_id: int):
        member = self.db.query(Member).get(member_id)
        if not member: raise ValueError("Member not found.")

        upcoming_sessions = self.db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.member_id == member_id,
            PersonalTrainingSession.status == SessionStatus.SCHEDULED,
            PersonalTrainingSession.scheduled_date >= date.today()
        ).order_by(PersonalTrainingSession.scheduled_date).all()

        from sqlalchemy.orm import joinedload
        upcoming_classes = self.db.query(ClassEnrollment).options(
            joinedload(ClassEnrollment.group_class)
        ).join(GroupClass).filter(
            ClassEnrollment.member_id == member_id,
            ClassEnrollment.attendance_status == AttendanceStatus.REGISTERED,
            GroupClass.scheduled_date >= date.today()
        ).order_by(GroupClass.scheduled_date).all()

        return {"member": member, "upcoming_sessions": upcoming_sessions, "upcoming_classes": upcoming_classes}

    def _is_trainer_available(self, trainer_id: int, check_date: date, start: time, end: time) -> bool:
        pt_conflict = self.db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.trainer_id == trainer_id,
            PersonalTrainingSession.scheduled_date == check_date,
            PersonalTrainingSession.start_time < end,
            PersonalTrainingSession.end_time > start,
            PersonalTrainingSession.status != SessionStatus.CANCELLED
        ).first()
        if pt_conflict: return False

        class_conflict = self.db.query(GroupClass).filter(
            GroupClass.trainer_id == trainer_id,
            GroupClass.scheduled_date == check_date,
            GroupClass.start_time < end,
            GroupClass.end_time > start
        ).first()
        if class_conflict: return False
        return True

    def _is_room_available(self, room_id: int, check_date: date, start: time, end: time) -> bool:
        pt_conflict = self.db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.room_id == room_id,
            PersonalTrainingSession.scheduled_date == check_date,
            PersonalTrainingSession.start_time < end,
            PersonalTrainingSession.end_time > start,
            PersonalTrainingSession.status != SessionStatus.CANCELLED
        ).first()
        if pt_conflict: return False

        class_conflict = self.db.query(GroupClass).filter(
            GroupClass.room_id == room_id,
            GroupClass.scheduled_date == check_date,
            GroupClass.start_time < end,
            GroupClass.end_time > start
        ).first()
        if class_conflict: return False
        return True

    # Helpers
    def get_all_members(self):
        return self.db.query(Member).all()
    
    def get_all_trainers(self):
        return self.db.query(Trainer).all()
        
    def get_all_rooms(self):
        return self.db.query(Room).all()
        
    def get_all_classes(self):
        return self.db.query(GroupClass).filter(GroupClass.scheduled_date >= date.today()).all()