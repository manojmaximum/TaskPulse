import logging
import time

from model import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.process_task")
def process_task(task_id, data):
    logger.info(f"Starting task {task_id}")
    for i in range(100):
        time.sleep(1)
        session = SessionLocal()
        test = session.query(Tasks).filter(Tasks.id == task_id).first()
        test.progress = i + 1
        session.commit()
        logger.info(f"Task {task_id} progress: {i + 1}")
    #Update the status flag after completed the progress
    db_session = SessionLocal() 
    status_detail = db_session.query(Tasks).filter(Tasks.id == task_id).first()
    status_detail.status = "completed"
    db_session.commit()
    #print the details to check the update progress
    detail = get_detail(task_id)
    print(detail.status,detail.progress,12121)
    logger.info(f"Completed task {task_id}")

def get_detail(task_id):
    session = SessionLocal()
    detail = session.query(Tasks).filter(Tasks.id == task_id).first()
    return detail