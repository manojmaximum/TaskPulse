import asyncio
import uuid

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from model import *

session = SessionLocal()

app = FastAPI()

class TaskRequest(BaseModel):
    data: str


@app.post("/submit-task/")
async def submit_task(request: TaskRequest):
    task_id = str(uuid.uuid4())
    query = Tasks(id=task_id, status="pending", progress=0)
    session.add(query)
    session.commit()
    session.flush()
    celery_app.send_task("tasks.process_task", args=[task_id, request.data])
    return {"task_id": task_id}


@app.get("/task-status/{task_id}")
async def task_status(task_id: str):
    task = session.query(Tasks).filter(Tasks.id == task_id).first()
    return {"task_id": task_id, "status": task.status, "progress": task.progress}


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    while True:
        task = get_detail(task_id)
        await websocket.send_json({"task_id": task_id, "progress": task.progress})
        await asyncio.sleep(1)
  

@app.websocket("/ws")
async def sample_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"message": "Hello World"})


def get_detail(task_id):
    session = SessionLocal()
    detail = session.query(Tasks).filter(Tasks.id == task_id).first()
    session.close()
    return detail