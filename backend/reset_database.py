from database.connection import engine, Base
from database.seed_data import seed_database
from models.member import Member
from models.trainer import Trainer
from models.room import Room
from models.admin_staff import AdminStaff
from models.group_class import GroupClass
from models.personal_training_session import PersonalTrainingSession
from models.class_enrollment import ClassEnrollment

""" Function to fully reset Database for testing purposes """

def reset():
    print("--- RESETTING DATABASE ---")
    # This deletes the broken tables so we can start fresh
    Base.metadata.drop_all(bind=engine)
    # This creates new tables and fills them with sample data
    seed_database()
    
    print("--- RESET COMPLETE ---")

if __name__ == "__main__":
    reset()