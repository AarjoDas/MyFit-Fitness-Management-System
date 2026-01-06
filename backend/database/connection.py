from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database Configuration
# Format: postgresql://<username>:<password>@<host>:<port>/<database_name>
DATABASE_URL = "postgresql+psycopg://postgres:student@localhost:5432/fitness_club_db"

engine = create_engine(DATABASE_URL)

# Create the SessionLocal Class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the Base Class
Base = declarative_base()

def get_db():
    """
    Dependency generator to get a database session.
    Useful if you expand to a web API later, or for context managers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()