import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.domain.repository import ContactsRepository, NotesRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def contacts_repo(session):
    return ContactsRepository(session)


@pytest.fixture
def notes_repo(session):
    return NotesRepository(session)
