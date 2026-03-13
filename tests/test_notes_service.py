import pytest

from app.application.notes_service import NotesService
from app.domain.models import Note
from app.domain.repository import NotesRepository


@pytest.fixture
def svc(notes_repo: NotesRepository) -> NotesService:
    return NotesService(notes_repo)


def test_create_note(svc: NotesService):
    note = svc.create_note("Shopping", "Buy milk")
    assert note.id is not None
    assert note.title == "Shopping"
    assert note.body == "Buy milk"


def test_create_note_empty_body(svc: NotesService):
    note = svc.create_note("Reminder")
    assert note.body == ""


def test_get_note(svc: NotesService):
    created = svc.create_note("Shopping", "Buy milk")
    found = svc.get_note(created.id)
    assert found.title == "Shopping"


def test_get_note_not_found(svc: NotesService):
    with pytest.raises(KeyError):
        svc.get_note(999)


def test_list_notes(svc: NotesService):
    svc.create_note("Note 1")
    svc.create_note("Note 2")
    notes = svc.list_notes()
    assert len(notes) == 2


def test_search_notes_by_title(svc: NotesService):
    svc.create_note("Shopping", "Buy milk")
    svc.create_note("Work", "Finish report")
    results = svc.search_notes("Shop")
    assert len(results) == 1
    assert results[0].title == "Shopping"


def test_search_notes_by_body(svc: NotesService):
    svc.create_note("Shopping", "Buy milk")
    svc.create_note("Work", "Finish report")
    results = svc.search_notes("milk")
    assert len(results) == 1


def test_search_notes_no_results(svc: NotesService):
    svc.create_note("Shopping", "Buy milk")
    results = svc.search_notes("nonexistent")
    assert results == []


def test_delete_note(svc: NotesService):
    created = svc.create_note("Shopping", "Buy milk")
    svc.delete_note(created.id)
    assert svc.list_notes() == []


def test_search_by_tag(notes_repo: NotesRepository):
    note = Note(title="Tagged", body="content")
    notes_repo.add_with_tags(note, ["urgent", "work"])

    results = notes_repo.search_by_tag("urgent")
    assert len(results) == 1
    assert results[0].title == "Tagged"


def test_search_by_tag_no_results(notes_repo: NotesRepository):
    note = Note(title="Tagged", body="content")
    notes_repo.add_with_tags(note, ["urgent"])

    results = notes_repo.search_by_tag("nonexistent")
    assert results == []


def test_add_with_tags_reuses_existing(notes_repo: NotesRepository):
    note1 = Note(title="Note 1")
    notes_repo.add_with_tags(note1, ["shared"])

    note2 = Note(title="Note 2")
    notes_repo.add_with_tags(note2, ["shared"])

    results = notes_repo.search_by_tag("shared")
    assert len(results) == 2
