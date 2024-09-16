import asyncio
import uuid
from contextlib import asynccontextmanager

import databases
import sqlalchemy
from celery import Celery
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./test.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

tasks = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("status", sqlalchemy.String),
    sqlalchemy.Column("progress", sqlalchemy.Integer),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


@asynccontextmanager
async def lifespan(application: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
celery_app = Celery("tasks", broker="redis://redis:6379/0")


class TaskRequest(BaseModel):
    data: str


@app.post("/submit-task/")
async def submit_task(request: TaskRequest):
    task_id = str(uuid.uuid4())
    query = tasks.insert().values(id=task_id, status="pending", progress=0)
    await database.execute(query)
    celery_app.send_task("tasks.process_task", args=[task_id, request.data])
    return {"task_id": task_id}


@app.get("/task-status/{task_id}")
async def task_status(task_id: str):
    query = tasks.select().where(tasks.c.id == task_id)
    task = await database.fetch_one(query)
    return {"task_id": task_id, "status": task["status"], "progress": task["progress"]}


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    while True:
        query = tasks.select().where(tasks.c.id == task_id)
        task = await database.fetch_one(query)
        await websocket.send_json({"task_id": task_id, "progress": task["progress"]})
        await asyncio.sleep(1)


@app.websocket("/ws")
async def sample_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"message": "Hello World"})
