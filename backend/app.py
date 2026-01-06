from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.connection import get_db
from services.member_service import MemberService
from services.trainer_service import TrainerService
from services.admin_service import AdminService
import schemas

app = FastAPI(title="Fitness Club API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Serialize member
        member_dict = {
            "member_id": data['member'].member_id,
            "first_name": data['member'].first_name,
            "last_name": data['member'].last_name,
            "email": data['member'].email,
        }
        
        # Serialize upcoming sessions
        sessions_list = []
        for session in data['upcoming_sessions']:
            sessions_list.append({
                "session_id": session.session_id,
                "scheduled_date": session.scheduled_date.isoformat() if session.scheduled_date else None,
                "start_time": str(session.start_time) if session.start_time else None,
                "end_time": str(session.end_time) if session.end_time else None,
                "room_id": session.room_id,
                "notes": session.notes,
            })
        
        # Serialize upcoming classes with group_class relationship
        classes_list = []
        for enrollment in data['upcoming_classes']:
            if enrollment.group_class:  # Check if relationship is loaded
                classes_list.append({
                    "enrollment_id": enrollment.enrollment_id,
                    "group_class": {
                        "class_id": enrollment.group_class.class_id,
                        "class_name": enrollment.group_class.class_name,
                        "scheduled_date": enrollment.group_class.scheduled_date.isoformat() if enrollment.group_class.scheduled_date else None,
                        "start_time": str(enrollment.group_class.start_time) if enrollment.group_class.start_time else None,
                    }
                })
        
        return {
            "member": member_dict,
            "upcoming_sessions": sessions_list,
            "upcoming_classes": classes_list
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

@app.post("/classes/enroll")
def enroll_in_class(enrollment: schemas.ClassEnrollmentCreate, service: MemberService = Depends(get_member_service)):
    """Register member for a group class"""
    try:
        return service.register_for_group_class(enrollment.member_id, enrollment.class_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/members/")
def list_all_members_for_selection(service: MemberService = Depends(get_member_service)):
    """Get all members for selection"""
    return service.get_all_members()

@app.get("/trainers/")
def list_all_trainers(service: MemberService = Depends(get_member_service)):
    """Get all trainers"""
    return service.get_all_trainers()

@app.get("/rooms/")
def list_all_rooms(service: MemberService = Depends(get_member_service)):
    """Get all rooms"""
    return service.get_all_rooms()

@app.get("/classes/")
def list_all_classes(service: MemberService = Depends(get_member_service)):
    """Get all available classes"""
    return service.get_all_classes()

# --- TRAINER ROUTES ---

@app.post("/trainers/schedule")
def get_trainer_schedule(request: schemas.TrainerScheduleRequest, service: TrainerService = Depends(get_trainer_service)):
    """Get trainer schedule for date range"""
    try:
        return service.get_trainer_schedule(request.trainer_id, request.start_date, request.end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/trainers/{trainer_id}/members/search")
def search_members(trainer_id: int, query: str, service: TrainerService = Depends(get_trainer_service)):
    """Search members by name"""
    # Validate that trainer exists
    trainers = service.get_all_trainers()
    trainer = next((t for t in trainers if t.trainer_id == trainer_id), None)
    if not trainer:
        raise HTTPException(status_code=404, detail=f"Trainer with ID {trainer_id} not found")
    # Search is global but we validate trainer access
    return service.search_members(query)

@app.get("/trainers/members/")
def list_all_members_for_trainer(service: TrainerService = Depends(get_trainer_service)):
    """Get all members for trainer to view"""
    return service.get_all_members()

@app.get("/trainers/members/{member_id}")
def view_member_profile(member_id: int, service: TrainerService = Depends(get_trainer_service)):
    """View member profile"""
    try:
        return service.view_member_profile(member_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/trainers/sessions/status")
def update_session_status(update: schemas.SessionStatusUpdate, service: TrainerService = Depends(get_trainer_service)):
    """Update PT session status"""
    try:
        return service.update_session_status(update.session_id, update.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/trainers/sessions/notes")
def update_session_notes(update: schemas.SessionNotesUpdate, service: TrainerService = Depends(get_trainer_service)):
    """Update PT session notes"""
    try:
        return service.update_session_notes(update.session_id, update.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- ADMIN ROUTES ---

@app.get("/admin/members")
def list_all_members(service: AdminService = Depends(get_admin_service)):
    """API version of Admin Portal Option 6"""
    return service.get_all_members()

@app.get("/admin/trainers")
def list_all_trainers_admin(service: AdminService = Depends(get_admin_service)):
    """List all trainers"""
    return service.get_all_trainers()

@app.get("/admin/rooms")
def list_all_rooms_admin(service: AdminService = Depends(get_admin_service)):
    """List all rooms"""
    return service.get_all_rooms()

@app.get("/admin/classes")
def list_all_classes_admin(service: AdminService = Depends(get_admin_service)):
    """List all classes"""
    return service.get_all_classes()

@app.post("/admin/rooms")
def add_room(room: schemas.RoomCreate, service: AdminService = Depends(get_admin_service)):
    """Add new room"""
    try:
        return service.add_room(room.name, room.capacity, room.room_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/trainers")
def add_trainer(trainer: schemas.TrainerCreate, service: AdminService = Depends(get_admin_service)):
    """Add new trainer"""
    try:
        return service.add_trainer(trainer.first_name, trainer.last_name, trainer.email, trainer.specialization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/classes")
def create_group_class(class_data: schemas.GroupClassCreate, service: AdminService = Depends(get_admin_service)):
    """Create new group class"""
    try:
        return service.create_group_class(
            class_data.name, class_data.trainer_id, class_data.room_id,
            class_data.scheduled_date, class_data.start_time, class_data.end_time,
            class_data.capacity
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/admin/classes/reschedule")
def reschedule_class(reschedule_data: schemas.GroupClassReschedule, service: AdminService = Depends(get_admin_service)):
    """Reschedule a group class"""
    try:
        return service.reschedule_class(
            reschedule_data.class_id, reschedule_data.new_date,
            reschedule_data.new_start, reschedule_data.new_end
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/admin/classes/{class_id}")
def cancel_class(class_id: int, service: AdminService = Depends(get_admin_service)):
    """API version of Admin Portal Option 5"""
    try:
        service.cancel_class(class_id)
        return {"message": "Class successfully cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))