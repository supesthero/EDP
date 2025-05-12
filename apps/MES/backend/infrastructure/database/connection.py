# infrastructure/database/connection.py
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session # Import Session from sqlmodel

# Load environment variables from .env file
load_dotenv() # Ensure .env is in the root of your backend or adjust path

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("CRITICAL: DATABASE_URL not found in .env. Application will not work correctly with a database.")
    # For local development without a .env, you might temporarily set a default for SQLite here,
    # but it's best practice to always use .env or other config management.
    # Example: DATABASE_URL = "sqlite:///./test_sqlmodel.db"
    # However, your project is configured for PostgreSQL.
    raise ValueError("DATABASE_URL environment variable not set.")


# Create a SQLModel/SQLAlchemy engine
# For production, consider connection pooling options like pool_size, max_overflow
engine = create_engine(DATABASE_URL, echo=False) # echo=True for debugging SQL queries

def get_session():
    """
    Dependency to get a database session.
    SQLModel uses SQLAlchemy sessions.
    """
    with Session(engine) as session:
        yield session

# Function to create all tables (useful for initial setup/testing if not using Alembic exclusively)
# SQLModel.metadata.create_all(engine) would be the SQLModel way if you were not using Alembic.
# Since we use Alembic, Alembic migrations are the source of truth for schema.
# This function might not be needed or should be used with caution.

# If you need to initialize SQLModel's metadata for some reason (e.g. for Alembic env.py)
# you would import your SQLModel table classes and then use SQLModel.metadata.
# from infrastructure.sqlmodels.work_order import WorkOrder # Example import

if __name__ == "__main__":
    print(f"Attempting to connect to: {DATABASE_URL}")
    try:
        with Session(engine) as session:
            # A simple query to test connection
            session.execute(text("SELECT 1")) # type: ignore
            print("Successfully connected to the database and executed a test query.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        print("Please ensure your DATABASE_URL in .env is correct, the database server is running, and the database itself exists.")
