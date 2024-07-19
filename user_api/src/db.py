from sqlalchemy import create_engine
from sqlmodel import SQLModel, create_engine

# Define your database URL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/app"


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)