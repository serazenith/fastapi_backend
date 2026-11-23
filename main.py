import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for ORM models."""

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))


class TaskORM(Base):
    """ORM model representing a task."""

    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


class CategoryORM(Base):
    """ORM model representing a category."""

    __tablename__ = "categories"

    name: Mapped[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI application."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

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
    completed: bool


class CreateTaskSchema(BaseModel):
    """Model representing a task to be created."""

    title: str


class UpdateTaskSchema(BaseModel):
    """Model representing a task to be updated."""

    title: str | None = None
    completed: bool | None = None


class CategorySchema(BaseModel):
    """Model representing a category."""

    id: str
    name: str


class CreateUpdateCategorySchema(BaseModel):
    """Model representing a category to be created or updated."""

    name: str


def get_db():
    """Function to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def taskorm_to_schema(taskorm: TaskORM) -> TaskSchema:
    """Function to convert a TaskORM object to a TaskSchema object."""
    return TaskSchema(id=taskorm.id, title=taskorm.title, completed=taskorm.completed)


def categoryorm_to_schema(categoryorm: CategoryORM) -> CategorySchema:
    return CategorySchema(id=categoryorm.id, name=categoryorm.name)


@app.get("/tasks", status_code=status.HTTP_200_OK, tags=["Tasks"])
def get_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    """Function to get all tasks."""
    tasks_orm = db.scalars(select(TaskORM)).all()
    return [taskorm_to_schema(task) for task in tasks_orm]


@app.post("/tasks", tags=["Tasks"], status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskSchema, db: Session = Depends(get_db)) -> TaskSchema:
    """Function to create a new task."""

    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return taskorm_to_schema(new_task)


@app.patch("/tasks/{id}", tags=["Tasks"], status_code=status.HTTP_200_OK)
def update_task(
    id: str, payload: UpdateTaskSchema, db: Session = Depends(get_db)
) -> TaskSchema:
    """Function to update a task."""

    task_to_update = db.get(TaskORM, id)
    if task_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if payload.title is not None:
        task_to_update.title = payload.title
    if payload.completed is not None:
        task_to_update.completed = payload.completed
    db.commit()
    db.refresh(task_to_update)
    return taskorm_to_schema(task_to_update)


@app.delete("/tasks/{id}", tags=["Tasks"], status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: str, db: Session = Depends(get_db)) -> None:
    """Function to delete a task."""
    task_to_delete = db.get(TaskORM, id)
    if task_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    db.delete(task_to_delete)
    db.commit()


# ________________________________________________________________________________________


@app.get("/categories", status_code=status.HTTP_200_OK, tags=["Categories"])
def get_categories(db: Session = Depends(get_db)) -> list[CategorySchema]:
    """Function to get all categories."""
    categories_orm = db.scalars(select(CategoryORM)).all()
    return [categoryorm_to_schema(category) for category in categories_orm]


@app.post("/categories", tags=["Categories"], status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CreateUpdateCategorySchema, db: Session = Depends(get_db)
) -> CategorySchema:
    """Function to create a new category."""

    new_category = CategoryORM(name=payload.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return categoryorm_to_schema(new_category)


@app.patch("/categories/{id}", tags=["Categories"], status_code=status.HTTP_200_OK)
def update_category(
    id: str, payload: CreateUpdateCategorySchema, db: Session = Depends(get_db)
) -> CategorySchema:
    """Function to update a category."""

    category_to_update = db.get(CategoryORM, id)
    if category_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    if payload.name is not None:
        category_to_update.name = payload.name
    db.commit()
    db.refresh(category_to_update)
    return categoryorm_to_schema(category_to_update)


@app.delete(
    "/categories/{id}", tags=["Categories"], status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(id: str, db: Session = Depends(get_db)) -> None:
    """Function to delete a category."""
    category_to_delete = db.get(CategoryORM, id)
    if category_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    db.delete(category_to_delete)
    db.commit()
