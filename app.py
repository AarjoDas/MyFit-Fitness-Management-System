from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.member_service import MemberService
from services.trainer_service import TrainerService
from services.admin_service import AdminService
import schemas

app = FastAPI(title="Fitness Club API")

# Dependency helpers to initialize services
def get_member_service(db: Session = Depends(get_db)):
    return MemberService(db)

def get_trainer_service(db: Session = Depends(get_db)):
    return TrainerService(db)

def get_admin_service(db: Session = Depends(get_db)):
    return AdminService(db)

# --- MEMBER ROUTES ---

@app.post("/members/", response_model=schemas.MemberResponse)
def register_member(member: schemas.MemberCreate, service: MemberService = Depends(get_member_service)):
    """API version of Member Portal Option 1"""
    try:
        return service.register_member(
            member.first_name, member.last_name, member.email, 
            member.date_of_birth, member.gender
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/members/{member_id}/dashboard")
def view_dashboard(member_id: int, service: MemberService = Depends(get_member_service)):
    """API version of Member Portal Option 2"""
    try:
        data = service.get_member_dashboard_data(member_id)
        return {
            "member": data['member'],
            "upcoming_sessions": data['upcoming_sessions'],
            "upcoming_classes": data['upcoming_classes']
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/sessions/pt")
def book_pt_session(session_data: schemas.PTSessionCreate, service: MemberService = Depends(get_member_service)):
    """API version of Member Portal Option 3"""
    try:
        return service.schedule_pt_session(
            session_data.member_id, session_data.trainer_id, session_data.room_id,
            session_data.scheduled_date, session_data.start_time, session_data.end_time,
            notes=session_data.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- ADMIN ROUTES ---

@app.get("/admin/members")
def list_all_members(service: AdminService = Depends(get_admin_service)):
    """API version of Admin Portal Option 6"""
    return service.get_all_members()

@app.delete("/admin/classes/{class_id}")
def cancel_class(class_id: int, service: AdminService = Depends(get_admin_service)):
    """API version of Admin Portal Option 5"""
    try:
        service.cancel_class(class_id)
        return {"message": "Class successfully cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))