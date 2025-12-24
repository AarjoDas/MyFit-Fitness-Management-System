# Health and Fitness Club Management System

**Author:** AARJO DAS 101349195  
**Date:** 2025-11-30  
**Course:** COMP 3005 - Final Project

## Project Overview & ORM Implementation

This project is a database application designed to manage the daily operations of a health and fitness club. The system allows for the management of members, trainers, group classes, and personal training sessions through a Command Line Interface (CLI).

This project utilizes SQLAlchemy, an Object-Relational Mapping (ORM) library for Python. Instead of writing raw SQL queries for every operation, the database interactions are handled through Python classes and objects.

**Mapping:** Each database table is represented by a Python class inheriting from a declarative Base.

**Relationships:** Foreign keys and table relationships (One-to-Many, Many-to-Many) are defined using SQLAlchemy's relationship and ForeignKey directives, allowing for intuitive navigation between objects (e.g., `trainer.pt_sessions`).

**Major Entities Mapped:**

- Member
- Trainer
- AdminStaff
- Room
- GroupClass
- PersonalTrainingSession
- ClassEnrollment

**ORM Code Sample (Entity Definition):**

```python
class Member(Base):
    __tablename__ = 'members'
    member_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    # Relationship definition
    pt_sessions = relationship("PersonalTrainingSession", back_populates="member")
```

## Application Architecture

The project follows a modular layered architecture to ensure separation of concerns:

**models/ – ORM Layer**

Defines the schema using SQLAlchemy classes (Member, Trainer, GroupClass, ClassEnrollment, Room, AdminStaff, etc.). This replaces manual DDL and automatically generates tables via metadata.

**services/ – Business Logic**

Implements validation, conflict detection, and transactional workflows:

- Prevents overlapping room bookings
- Validates trainer availability
- Enforces class capacity
- Manages registration logic

**client/ – Presentation Layer**

Provides a CLI with dedicated menus for Members, Trainers, and Admin Staff to interact with the system.

**database/ – Data Layer**

Handles the engine configuration, session factory, triggers, indexing, and prepopulated seed data.

## Features & Functionality

The application supports three distinct user roles with specific permissions:

**Member Functions**

- Create a new profile and update personal information.
- View upcoming personal training sessions and class enrollments.
- Book personal training sessions with availability checks.
- Register for classes, adhering to capacity and schedule constraints.

**Trainer Functions**

- View a chronological schedule of assigned group classes and PT sessions.
- Look up member profiles (read-only) to track client progress.
- Mark scheduled sessions as completed, cancelled, or no-show.

**Administrative Functions**

- Add new rooms and hire trainers.
- Create and modify group classes (assigning trainer, room, and timeslot).
- Cancel classes and manage rescheduling.
- Generate reports for all members and trainers.

## ER Model

**Assumptions:**

- A Solo Project scope was used, meeting the minimum requirement of at least 6 Entities, 5 Relationships and 8 Operations.
- ClassEnrollment is modeled as an associative entity to track specific registration dates and statuses.
- A Personal Training Session belongs to exactly one member and one trainer.

## ER to Relational Mapping

The ER model was translated into a relational schema using SQLAlchemy's declarative mapping system:

- **Entity -> Class:** Every entity box in the ERD corresponds to a Class in the models/ directory.
- **Attribute -> Column:** ER attributes became Class attributes using Column().
- **Relationship -> ForeignKey:** Lines in the ERD were converted to ForeignKey fields on the "Many" side of 1:N relationships.

## Normalization Proof (2NF and 3NF)

The schema satisfies 2NF and 3NF. Evidence is summarized below:

**First Normal Form (1NF)**

- All tables contain atomic, indivisible attributes.
- No repeating groups or multivalued attributes exist.

**Second Normal Form (2NF)**

For all non-key attributes A and composite keys K, there is no partial dependency.

Example: In ClassEnrollment(enrollment_id, class_id, member_id...), the Primary Key is the atomic enrollment_id. Therefore, no attribute can depend on only "part" of the key.

Conclusion: All tables utilize surrogate keys (single column IDs), making partial dependency impossible. Therefore, all tables meet 2NF.

**Third Normal Form (3NF)**

For every non-key attribute A, A does not depend on another non-key attribute (no transitive dependency).

- **Member Table:** Attributes like email, first_name, and gender depend only on member_id.
- **Room Table:** Attributes like room_name, room_type, and capacity depend solely on room_id.
- **GroupClass Table:** trainer_id and room_id are foreign keys but do not determine other non-key attributes like capacity within this specific table context.

Conclusion: Every table is in 3NF.

## Database Definition (ORM)

Since this project uses an ORM, traditional DDL files are replaced by Python Model definitions.

**Entity Class Definition (Example: group_class.py):**

```python
class GroupClass(Base):
    __tablename__ = 'group_classes'
    
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(200), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.trainer_id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False)
    
    # ORM relationships for easy data access
    trainer = relationship("Trainer", back_populates="group_classes")
    enrollments = relationship("ClassEnrollment", back_populates="group_class")
```

**Table Creation & Seeding:**

Tables are created programmatically using Base.metadata.create_all(bind=engine). Data is seeded using object instantiation:

```python
# database/seed_data.py
def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create objects
    t1 = Trainer(first_name="John", last_name="Doe", specialization="HIIT")
    r1 = Room(room_name="Cardio Zone", capacity=50)
    
    # Insert via ORM Session
    session.add_all([t1, r1])
    session.commit()
```

## Functionality Demonstration (Code Walkthrough)

This section highlights the backend logic for key operations required by the assignment.

**Role: Member**

**Operation: Book Personal Training Session**

Logic: Checks if the Trainer and Room are available at the requested time. If valid, creates a session.

- Success Case: Booking a slot where the trainer has no conflicts.
- Edge Case: Attempting to book a time when the Room is already occupied by a Group Class.

Backend Logic (services/member_service.py):

```python
def schedule_pt_session(self, member_id, trainer_id, room_id, date, start, end, notes):
    # Validation via internal helper methods
    if not self._is_trainer_available(trainer_id, date, start, end):
        raise ValueError("Trainer is not available.")
    
    # Object creation
    new_session = PersonalTrainingSession(
        member_id=member_id,
        trainer_id=trainer_id,
        status=SessionStatus.SCHEDULED,
        notes=notes
    )
    self.db.add(new_session)
    self.db.commit()
```

**Role: Trainer**

**Operation: View Schedule**

Logic: Queries both GroupClass and PersonalTrainingSession tables for the specific trainer ID and merges the results chronologically.

Backend Logic (services/trainer_service.py):

```python
def get_trainer_schedule(self, trainer_id, start_date, end_date):
    # ORM Query
    classes = self.db.query(GroupClass).filter(
        GroupClass.trainer_id == trainer_id, ...
    ).all()
    # ... logic to combine and format list ...
    return schedule
```

**Role: Admin**

**Operation: Reschedule Group Class**

Logic: Updates the time/date of an existing class after verifying resource availability for the new slot.

Backend Logic (services/admin_service.py):

```python
def reschedule_class(self, class_id, new_date, new_start, new_end):
    group_class = self.db.query(GroupClass).get(class_id)
    
    # Conflict Check
    if not self._is_room_available(group_class.room_id, new_date, new_start, new_end):
        raise ValueError("Room is not available.")

    group_class.scheduled_date = new_date
    self.db.commit() # Update happens on commit
```

## Installation & Running

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Setup Database (Create & Seed):**

```bash
python -m reset_database
```

**Run Application:**

```bash
python main.py
```

whaddup mud