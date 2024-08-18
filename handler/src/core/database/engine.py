from sqlalchemy import create_engine

from src.config import settings


engine = create_engine(str(settings.SQL_DATABASE_URI))  # pool_pre_ping=True
