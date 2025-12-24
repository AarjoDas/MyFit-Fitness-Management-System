from datetime import datetime
from services.admin_service import AdminService

def run(service: AdminService):
    while True:
        print("\n--- Admin Portal ---")
        print("1. Add New Room")
        print("2. Add New Trainer")
        print("3. Create Group Class")
        print("4. Reschedule Group Class")
        print("5. Cancel Group Class")
        print("6. List All Members")
        print("7. List All Trainers")
        print("8. Back to Main Menu")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            name = input("Room Name: ")
            try:
                cap_input = input("Capacity: ")
                if not cap_input: raise ValueError("Empty")
                cap = int(cap_input)
                
                rtype = input("Type (Cardio/Weights/Studio): ")
                service.add_room(name, cap, rtype)
                print("Room added.")
            except ValueError:
                print("Error: Capacity must be a valid number.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '2':
            first = input("First Name: ")
            last = input("Last Name: ")
            email = input("Email: ")
            spec = input("Specialization: ")
            try:
                t = service.add_trainer(first, last, email, spec)
                print(f"Trainer added. ID: {t.trainer_id}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '3':
            _create_class(service)

        elif choice == '4':
            _reschedule_class(service)

        elif choice == '5':
            _cancel_class(service)

        elif choice == '6':
            _list_members(service)

        elif choice == '7':
            _list_trainers(service)

        elif choice == '8':
            break

def _print_list(title, items, formatter):
    print(f"\n--- {title} ---")
    if not items: print("None found.")
    for item in items:
        print(formatter(item))
    print("-------------------")

def _list_members(service):
    members = service.get_all_members()
    _print_list("All Registered Members", members, lambda m: f"ID: {m.member_id} | {m.first_name} {m.last_name} | {m.email}")

def _list_trainers(service):
    trainers = service.get_all_trainers()
    _print_list("All Trainers", trainers, lambda t: f"ID: {t.trainer_id} | {t.first_name} {t.last_name} | Spec: {t.specialization}")

def _create_class(service):
    print("\n--- Create New Class ---")
    _print_list("Trainers", service.get_all_trainers(), lambda t: f"ID: {t.trainer_id} | {t.first_name} {t.last_name}")
    _print_list("Rooms", service.get_all_rooms(), lambda r: f"ID: {r.room_id} | {r.room_name} (Cap: {r.capacity})")

    name = input("Class Name: ")
    if not name.strip():
        print("Error: Class Name cannot be empty.")
        return

    try:
        tid_input = input("Trainer ID: ")
        if not tid_input.strip(): raise ValueError("Trainer ID missing")
        tid = int(tid_input)

        rid_input = input("Room ID: ")
        if not rid_input.strip(): raise ValueError("Room ID missing")
        rid = int(rid_input)

        cap_input = input("Capacity: ")
        if not cap_input.strip(): raise ValueError("Capacity missing")
        cap = int(cap_input)
        
        date_str = input("Date (YYYY-MM-DD): ")
        start_str = input("Start Time (HH:MM:SS): ")
        end_str = input("End Time (HH:MM:SS): ")
        
        s_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        s_time = datetime.strptime(start_str, "%H:%M:%S").time()
        e_time = datetime.strptime(end_str, "%H:%M:%S").time()
        
        new_class = service.create_group_class(name, tid, rid, s_date, s_time, e_time, cap)
        print(f"Class Created! ID: {new_class.class_id}")
        
    except ValueError as ve:
        if "invalid literal" in str(ve) or "missing" in str(ve):
             print("Error: Please enter valid numbers for IDs and Capacity.")
        elif "time data" in str(ve):
             print("Error: Incorrect Date/Time format. Use YYYY-MM-DD and HH:MM:SS.")
        else:
             print(f"Input Error: {ve}")
    except Exception as e:
        print(f"Creation Failed: {e}")

def _cancel_class(service):
    _print_list("Active Classes", service.get_all_classes(), lambda c: f"ID: {c.class_id} | {c.class_name} | {c.scheduled_date}")

    cid_input = input("Class ID to cancel: ")
    try:
        if not cid_input.strip(): return
        service.cancel_class(int(cid_input))
        print("Class cancelled.")
    except ValueError:
        print("Error: Class ID must be a number.")
    except Exception as e:
        print(f"Error: {e}")

def _reschedule_class(service):
    print("\n--- Reschedule Group Class ---")
    _print_list("Active Classes", service.get_all_classes(), 
                lambda c: f"ID: {c.class_id} | {c.class_name} | {c.scheduled_date} {c.start_time}-{c.end_time}")

    try:
        cid_input = input("Enter Class ID to reschedule: ")
        if not cid_input.strip(): return
        class_id = int(cid_input)
        
        print("\n--- Enter New Schedule ---")
        date_str = input("New Date (YYYY-MM-DD): ")
        start_str = input("New Start Time (HH:MM:SS): ")
        end_str = input("New End Time (HH:MM:SS): ")
        
        new_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        new_start = datetime.strptime(start_str, "%H:%M:%S").time()
        new_end = datetime.strptime(end_str, "%H:%M:%S").time()
        
        service.reschedule_class(class_id, new_date, new_start, new_end)
        print("Success! Class rescheduled.")
        
    except ValueError as ve:
        if "time data" in str(ve):
             print("Error: Incorrect Date/Time format.")
        elif "invalid literal" in str(ve):
             print("Error: Class ID must be a number.")
        else:
             print(f"Input Error: {ve}")
    except Exception as e:
        print(f"Reschedule Failed: {e}")