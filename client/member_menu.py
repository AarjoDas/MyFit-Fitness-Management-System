from datetime import datetime
from services.member_service import MemberService

def run(service: MemberService):
    while True:
        print("\n--- MEMBER MENU ---")
        print("1. Register New Member")
        print("2. Login (View Dashboard)")
        print("3. Book Personal Training Session")
        print("4. Register for Group Class")
        print("5. Back to Main Menu")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            _register_member(service)
        elif choice == '2':
            _view_dashboard(service)
        elif choice == '3':
            _book_pt(service)
        elif choice == '4':
            _book_class(service)
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

def _print_list(title, items, formatter):
    print(f"\n--- {title} ---")
    if not items:
        print("No records found.")
    for item in items:
        print(formatter(item))
    print("-----------------------")

def _register_member(service):
    print("\n--- REGISTER NEW MEMBER ---")
    email = input("Email: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    dob_str = input("Date of Birth (YYYY-MM-DD): ")
    gender_input = input("Gender (Male/Female/Other): ")
    gender = gender_input.capitalize()
    
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        member = service.register_member(first_name, last_name, email, dob, gender)
        print(f"Member registered successfully! ID: {member.member_id}")
    except Exception as e:
        print(f"Error: {e}")

def _view_dashboard(service):
    # Display members so user can pick their ID
    _print_list("Available Members", service.get_all_members(), 
                lambda m: f"ID: {m.member_id} | {m.first_name} {m.last_name}")

    mid = input("Enter Your Member ID: ")
    try:
        member_id = int(mid)
        data = service.get_member_dashboard_data(member_id)
        
        print(f"\nWelcome back, {data['member'].first_name}!")
        print(f"Email: {data['member'].email}")
        
        print("\n--- Upcoming PT Sessions ---")
        if not data['upcoming_sessions']:
            print("No upcoming sessions.")
        for s in data['upcoming_sessions']:
            # Display notes if they exist
            notes_display = f" | Notes: {s.notes}" if s.notes else ""
            print(f"- {s.scheduled_date} @ {s.start_time} (Room ID: {s.room_id}){notes_display}")
            
        print("\n--- Upcoming Classes ---")
        if not data['upcoming_classes']:
            print("No upcoming classes.")
        for c in data['upcoming_classes']:
            cls = c.group_class 
            print(f"- {cls.class_name}: {cls.scheduled_date} @ {cls.start_time}")
            
    except Exception as e:
        print(f"Error loading dashboard: {e}")

def _book_pt(service):
    # Show everything needed to make a booking
    _print_list("Your Member ID", service.get_all_members(), lambda m: f"ID: {m.member_id} | {m.first_name}")
    _print_list("Trainers", service.get_all_trainers(), lambda t: f"ID: {t.trainer_id} | {t.first_name} {t.last_name} ({t.specialization})")
    _print_list("Rooms", service.get_all_rooms(), lambda r: f"ID: {r.room_id} | {r.room_name}")

    try:
        mid_in = input("Member ID: ")
        if not mid_in.strip(): return
        mid = int(mid_in)

        tid_in = input("Trainer ID: ")
        if not tid_in.strip(): return
        tid = int(tid_in)

        rid_in = input("Room ID: ")
        if not rid_in.strip(): return
        rid = int(rid_in)

        date_str = input("Date (YYYY-MM-DD): ")
        start_str = input("Start Time (HH:MM:SS): ")
        end_str = input("End Time (HH:MM:SS): ")

        notes_input = input("Enter Notes (optional - type 'N/A' to skip): ")
        if not notes_input.strip() or notes_input.strip().upper() == "N/A":
            notes = None
        else:
            notes = notes_input.strip()

        s_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        s_time = datetime.strptime(start_str, "%H:%M:%S").time()
        e_time = datetime.strptime(end_str, "%H:%M:%S").time()

        session = service.schedule_pt_session(mid, tid, rid, s_date, s_time, e_time, notes=notes)
        print(f"Session Booked! ID: {session.session_id}")
    except ValueError as ve:
         print(f"Input Error: {ve}")
    except Exception as e:
        print(f"Booking Failed: {e}")

def _book_class(service):
    _print_list("Your Member ID", service.get_all_members(), lambda m: f"ID: {m.member_id} | {m.first_name}")
    _print_list("Available Classes", service.get_all_classes(), lambda c: f"ID: {c.class_id} | {c.class_name} | {c.scheduled_date} @ {c.start_time}")

    try:
        mid_in = input("Member ID: ")
        if not mid_in.strip(): return
        mid = int(mid_in)

        cid_in = input("Class ID: ")
        if not cid_in.strip(): return
        cid = int(cid_in)

        enrollment = service.register_for_group_class(mid, cid)
        print(f"Successfully enrolled in Class ID {cid}. Enrollment ID: {enrollment.enrollment_id}")
    except ValueError:
        print("Error: IDs must be numbers.")
    except Exception as e:
        print(f"Enrollment Failed: {e}")