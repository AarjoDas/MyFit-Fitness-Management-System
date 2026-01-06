from datetime import datetime
from services.trainer_service import TrainerService

def run(service: TrainerService):
    while True:
        print("\n--- Trainer Portal ---")
        print("1. View My Schedule")
        print("2. Search/View Member Profile")
        print("3. Update Session Status (Mark Complete/No-Show)")
        print("4. Back to Main Menu")

        choice = input("Select an option: ")

        if choice == '1':
            _view_schedule(service)
        elif choice == '2':
            _search_member(service)
        elif choice == '3':
            _update_status(service)
        elif choice == '4':
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

def _view_schedule(service):
    # Display Trainers so the user knows their own ID
    _print_list("Trainers List", service.get_all_trainers(), 
                lambda t: f"ID: {t.trainer_id} | Name: {t.first_name} {t.last_name}")

    tid = input("Enter YOUR Trainer ID: ")
    start_str = input("Start Date (YYYY-MM-DD): ")
    end_str = input("End Date (YYYY-MM-DD): ")
    
    try:
        s_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        e_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        
        schedule = service.get_trainer_schedule(int(tid), s_date, e_date)
        
        print(f"\nSchedule for Trainer {tid}:")
        if not schedule:
            print("No sessions found.")
        
        for item in schedule:
            # Show Status in the output so they can see if it's already Completed
            status_str = f"[{item.get('status', 'N/A')}]" if 'status' in item else ""
            print(f"[{item['date']} {item['start_time']}-{item['end_time']}] {status_str} {item['type']}: {item['name']} (Room: {item['room']}) - ID: {item['id']}")
            
    except Exception as e:
        print(f"Error: {e}")

def _search_member(service):
    _print_list("All Members", service.get_all_members(), 
                lambda m: f"ID: {m.member_id} | {m.first_name} {m.last_name} | {m.email}")

    print("Options:")
    print("1. Select Member by ID (from list above)")
    print("2. Search by Name")
    opt = input("Choice: ")

    view_id = None
    
    if opt == '2':
        name = input("Enter Member Name to search: ")
        results = service.search_members(name)
        if not results:
            print("No members found.")
            return
        _print_list("Search Results", results, lambda m: f"ID: {m.member_id} | {m.first_name} {m.last_name}")
        view_id = input("\nEnter ID to view full profile: ")
    else:
        view_id = input("Enter Member ID: ")

    if view_id:
        try:
            profile = service.view_member_profile(int(view_id))
            print(f"\n--- Profile: {profile['full_name']} ---")
            print(f"Email: {profile['email']}")
            print(f"Gender: {profile['gender']}")
            print("Recent Activity:")
            if not profile['recent_activity']:
                print("  - No recent activity.")
            for act in profile['recent_activity']:
                print(f"  - {act}")
        except Exception as e:
            print(f"Error: {e}")

def _update_status(service):
    print("\n--- Update Session Status ---")
    print("Tip: Use 'View My Schedule' to find the Session ID.")
    
    sid_in = input("Enter Session ID: ")
    if not sid_in.strip(): return
    
    print("\nSelect New Status:")
    print("1. Completed")
    print("2. No Show")
    print("3. Cancelled")
    print("4. Scheduled (Reset)")
    
    status_choice = input("Choice: ").strip()
    status_map = {
        '1': 'Completed',
        '2': 'No Show',
        '3': 'Cancelled',
        '4': 'Scheduled'
    }
    
    new_status = status_map.get(status_choice)
    if not new_status:
        print("Invalid status choice.")
        return

    try:
        updated_session = service.update_session_status(int(sid_in), new_status)
        print(f"Success! Session {updated_session.session_id} marked as '{updated_session.status.value}'.")
        
    except Exception as e:
        print(f"Error: {e}")