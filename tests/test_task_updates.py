import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from main import Base, TaskORM, UpdateTaskSchema, update_task


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.mark.parametrize("changes", [{}, {"title": "Updated"}, {"completed": False}])
def test_missing_task_returns_404(db, changes):
    with pytest.raises(HTTPException) as error:
        update_task("missing", UpdateTaskSchema(**changes), db)

    assert error.value.status_code == 404
    assert error.value.detail == "Task not found"


@pytest.mark.parametrize(
    ("changes", "expected_title", "expected_completed"),
    [
        ({"title": "Updated"}, "Updated", True),
        ({"completed": False}, "Original", False),
        ({"title": "Updated", "completed": False}, "Updated", False),
        ({}, "Original", True),
    ],
)
def test_partial_update_is_persisted(db, changes, expected_title, expected_completed):
    task = TaskORM(title="Original", completed=True)
    db.add(task)
    db.commit()
    task_id = task.id

    result = update_task(task_id, UpdateTaskSchema(**changes), db)

    assert result.id == task_id
    assert result.title == expected_title
    assert result.completed is expected_completed

    # Use a new session to check committed data rather than cached ORM attributes.
    with Session(db.get_bind()) as verification_db:
        saved_task = verification_db.get(TaskORM, task_id)
        assert saved_task is not None
        assert saved_task.title == expected_title
        assert saved_task.completed is expected_completed
