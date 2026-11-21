import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskSchema(BaseModel):
    """Model representing a task."""

    id: str
    title: str
    completed: bool | None = False


class CreateTaskSchema(BaseModel):
    """Model representing a task to be created."""

    title: str


class UpdateTaskSchema(BaseModel):
    """Model representing a task to be updated."""

    title: str | None = None
    completed: bool | None = None


tasks: list[TaskSchema] = []


@app.get("/tasks", tags=["Tasks"])
def get_tasks() -> list[TaskSchema]:
    """Function to get all tasks."""
    return tasks


@app.post("/tasks", tags=["Tasks"], status_code=201)
def create_task(payload: CreateTaskSchema) -> TaskSchema:
    """Function to create a new task."""
    new_task = TaskSchema(id=str(uuid.uuid4()), title=payload.title, completed=False)
    tasks.append(new_task)
    return new_task

