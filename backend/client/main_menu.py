import sys
from database.connection import SessionLocal
from services.member_service import MemberService
from services.trainer_service import TrainerService
from services.admin_service import AdminService
from client import member_menu, trainer_menu, admin_menu

def main():
    # Initialize Database Session
    db = SessionLocal()
    
    # Initialize Services
    member_service = MemberService(db)
    trainer_service = TrainerService(db)
    admin_service = AdminService(db)

    while True:
        print("\n=== Health & Fitness Club Management System ===")
        print("1. Member Portal")
        print("2. Trainer Portal")
        print("3. Admin Portal")
        print("4. Exit")
        
        choice = input("Select an option: ")

        if choice == '1':
            member_menu.run(member_service)
        elif choice == '2':
            trainer_menu.run(trainer_service)
        elif choice == '3':
            admin_menu.run(admin_service)
        elif choice == '4':
            print("Exiting system. Goodbye!")
            db.close()
            sys.exit()
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()