# database/schema_extras.py
from sqlalchemy import text, Index, DDL, event
from database.connection import engine
from models.member import Member
from models.group_class import GroupClass
from models.personal_training_session import PersonalTrainingSession
from models.class_enrollment import ClassEnrollment

def create_schema_extras():
    """
    Create views, triggers, and indexes using SQLAlchemy ORM constructs.
    """
    print("Applying schema extras (Views, Triggers, Indexes)...")

    with engine.connect() as conn:
        # Creates Indexes if they dont exist
        indexes = [
            Index('idx_member_email', Member.email),
            Index('idx_class_date', GroupClass.scheduled_date),
            Index('idx_pt_sessions_date', PersonalTrainingSession.scheduled_date),
            Index('idx_enrollment_member_class', ClassEnrollment.member_id, ClassEnrollment.class_id),
            Index('idx_enrollment_status', ClassEnrollment.attendance_status)
        ]

        for idx in indexes:
            try:
                #check DB before creating
                idx.create(bind=engine, checkfirst=True)
                print(f"Index '{idx.name}' verified.")
            except Exception as e:
                print(f"Skipping index '{idx.name}': {e}")

        # Views
        view_sql = DDL("""
        CREATE OR REPLACE VIEW member_enrollment_summary AS
        SELECT 
            m.member_id,
            m.first_name || ' ' || m.last_name AS member_name,
            COUNT(ce.enrollment_id) AS total_classes_enrolled,
            COUNT(CASE WHEN gc.scheduled_date > CURRENT_DATE THEN 1 END) AS upcoming_classes
        FROM members m
        LEFT JOIN class_enrollments ce ON m.member_id = ce.member_id 
            AND ce.attendance_status IN ('Registered', 'Attended')
        LEFT JOIN group_classes gc ON ce.class_id = gc.class_id
        GROUP BY m.member_id, m.first_name, m.last_name;
        """)
        
        conn.execute(view_sql)
        print("View 'member_enrollment_summary' created/updated.")

        # Trigger
        func_sql = DDL("""
        CREATE OR REPLACE FUNCTION check_room_availability()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Check for overlapping PT sessions
            IF EXISTS (
                SELECT 1 FROM personal_training_sessions 
                WHERE room_id = NEW.room_id 
                AND scheduled_date = NEW.scheduled_date 
                AND session_id != COALESCE(NEW.session_id, -1)
                AND status != 'Cancelled'
                AND start_time < NEW.end_time 
                AND end_time > NEW.start_time
            ) THEN
                RAISE EXCEPTION 'Room already booked for a PT session at this time';
            END IF;
            
            -- Check for overlapping group classes
            IF EXISTS (
                SELECT 1 FROM group_classes 
                WHERE room_id = NEW.room_id 
                AND scheduled_date = NEW.scheduled_date 
                AND class_id != COALESCE(NEW.class_id, -1)
                AND start_time < NEW.end_time 
                AND end_time > NEW.start_time
            ) THEN
                RAISE EXCEPTION 'Room already booked for a group class at this time';
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

        trigger_pt_sql = DDL("""
        CREATE OR REPLACE TRIGGER room_booking_check_pt
            BEFORE INSERT OR UPDATE ON personal_training_sessions
            FOR EACH ROW EXECUTE FUNCTION check_room_availability();
        """)

        trigger_class_sql = DDL("""
        CREATE OR REPLACE TRIGGER room_booking_check_class
            BEFORE INSERT OR UPDATE ON group_classes
            FOR EACH ROW EXECUTE FUNCTION check_room_availability();
        """)

        conn.execute(func_sql)
        conn.execute(trigger_pt_sql)
        conn.execute(trigger_class_sql)
        print("Trigger 'check_room_availability' created/updated.")
        
        conn.commit()