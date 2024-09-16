import logging
import time

import sqlalchemy
from celery import Celery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DATABASE_URL = "sqlite:///./test.db"
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata = sqlalchemy.MetaData()

tasks = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("status", sqlalchemy.String),
    sqlalchemy.Column("progress", sqlalchemy.Integer),
)

metadata.create_all(engine)
celery_app = Celery("tasks", broker="redis://redis:6379/0")


@celery_app.task(name="tasks.process_task")
def process_task(task_id, data):
    logger.info(f"Starting task {task_id}")
    with engine.connect() as connection:
        for i in range(100):
            time.sleep(1)
            query = tasks.update().where(tasks.c.id == task_id).values(progress=i + 1)
            connection.execute(query)
            logger.info(f"Task {task_id} progress: {i + 1}")
        query = tasks.update().where(tasks.c.id == task_id).values(status="completed")
        connection.execute(query)
    logger.info(f"Completed task {task_id}")
