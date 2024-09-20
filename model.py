import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

DATABASE_URL = "sqlite:////data/test.db"
engine = sqlalchemy.create_engine(DATABASE_URL,  connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = sqlalchemy.MetaData()

celery_app = Celery("tasks", broker="redis://redis:6379/0")

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    status = Column(String)
    progress = Column(Integer) 



# Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

Base.metadata.create_all(bind=engine)