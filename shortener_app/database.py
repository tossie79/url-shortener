from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings




settings = get_settings()
# Create the database engine
engine = create_engine(settings.db_url, connect_args={"check_same_thread": False})
# Create a base class for declarative models
Base = declarative_base()
# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



###################################