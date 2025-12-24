from datetime import date, time
from database.connection import SessionLocal, engine, Base
from models.member import Member, GenderEnum
from models.trainer import Trainer
from models.room import Room
from models.admin_staff import AdminStaff 
from models.group_class import GroupClass

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    if session.query(Room).first():
        print("Database already contains data. Skipping seed.")
        session.close()
        return

    print("Seeding data...")

    # --- Add Rooms ---
    r1 = Room(room_name="Cardio Zone", capacity=50, room_type="Cardio")
    r2 = Room(room_name="Weight Room", capacity=40, room_type="Weights")
    r3 = Room(room_name="Yoga Studio", capacity=20, room_type="Studio")
    session.add_all([r1, r2, r3])
    session.commit()

    # --- Add Trainers ---
    t1 = Trainer(first_name="John", last_name="Doe", email="john@fit.com", specialization="HIIT", hire_date=date(2023, 1, 15))
    t2 = Trainer(first_name="Sarah", last_name="Connor", email="sarah@fit.com", specialization="Strength", hire_date=date(2023, 3, 10))
    session.add_all([t1, t2])
    session.commit()

    # --- Add Members ---
    m1 = Member(first_name="Alice", last_name="Smith", email="alice@test.com", date_of_birth=date(1995, 5, 20), gender=GenderEnum.MALE, registration_date=date.today())
    m2 = Member(first_name="Bob", last_name="Jones", email="bob@test.com", date_of_birth=date(1990, 8, 15), gender=GenderEnum.FEMALE, registration_date=date.today())
    session.add_all([m1, m2])
    session.commit()

    # --- Add Admin ---
    a1 = AdminStaff(first_name="Admin", last_name="User", email="admin@fit.com", role="Manager", hire_date=date.today())
    session.add(a1)
    session.commit()

    # --- Add a Sample Class ---
    c1 = GroupClass(
        class_name="Morning Yoga",
        trainer_id=t1.trainer_id,
        room_id=r3.room_id,
        scheduled_date=date.today(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        capacity=15
    )
    session.add(c1)
    session.commit()

    print("Seeding Complete!")
    print(f"Added: 3 Rooms, 2 Trainers, 2 Members, 1 Admin, 1 Class")
    print("You can now run 'python main.py'")
    session.close()

if __name__ == "__main__":
    seed_database()