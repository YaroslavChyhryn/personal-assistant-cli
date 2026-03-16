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
    assert created.id is not None
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
    assert created.id is not None
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


def test_create_note_with_tags(svc: NotesService):
    note = svc.create_note("Tagged", "content", tags=["urgent", "work"])
    assert len(note.tags) == 2
    tag_names = {t.name for t in note.tags}
    assert tag_names == {"urgent", "work"}


def test_update_note(svc: NotesService):
    created = svc.create_note("Old Title", "Old body")
    assert created.id is not None
    updated = svc.update_note(created.id, title="New Title", body="New body")
    assert updated.title == "New Title"
    assert updated.body == "New body"


def test_update_note_partial(svc: NotesService):
    created = svc.create_note("Title", "Body")
    assert created.id is not None
    updated = svc.update_note(created.id, title="New Title")
    assert updated.title == "New Title"
    assert updated.body == "Body"


def test_add_tags_to_existing_note(svc: NotesService):
    created = svc.create_note("Note", "content")
    assert created.id is not None
    updated = svc.add_tags(created.id, ["python", "dev"])
    assert len(updated.tags) == 2


def test_remove_tag_from_note(svc: NotesService):
    created = svc.create_note("Note", "content", tags=["python", "dev"])
    assert created.id is not None
    updated = svc.remove_tag(created.id, "python")
    assert len(updated.tags) == 1
    assert updated.tags[0].name == "dev"


def test_note_title_validation_rejects_empty():
    with pytest.raises(ValueError, match="Note title cannot be empty"):
        Note.model_validate({"title": ""})


def test_note_title_validation_rejects_whitespace():
    with pytest.raises(ValueError, match="Note title cannot be empty"):
        Note.model_validate({"title": "   "})


def test_tag_name_validation_rejects_empty():
    from app.domain.models import Tag

    with pytest.raises(ValueError, match="Tag name cannot be empty"):
        Tag.model_validate({"name": ""})


def test_update_note_validates_empty_title(svc: NotesService):
    created = svc.create_note("Title", "Body")
    assert created.id is not None
    with pytest.raises(ValueError, match="Note title cannot be empty"):
        svc.update_note(created.id, title="")


# ── Sort / Group by tags ─────────────────────────────────────────────


def test_notes_grouped_by_tag(svc: NotesService):
    svc.create_note("Work task", tags=["work"])
    svc.create_note("Home task", tags=["home"])
    svc.create_note("Both", tags=["work", "home"])

    grouped = svc.notes_grouped_by_tag()
    assert "work" in grouped
    assert "home" in grouped
    assert len(grouped["work"]) == 2  # "Work task" + "Both"
    assert len(grouped["home"]) == 2  # "Home task" + "Both"


def test_notes_grouped_by_tag_empty(svc: NotesService):
    grouped = svc.notes_grouped_by_tag()
    assert grouped == {}


def test_untagged_notes(svc: NotesService):
    svc.create_note("Tagged", tags=["work"])
    svc.create_note("Not tagged")

    untagged = svc.untagged_notes()
    assert len(untagged) == 1
    assert untagged[0].title == "Not tagged"


def test_untagged_notes_empty_when_all_tagged(svc: NotesService):
    svc.create_note("Note", tags=["tag1"])
    assert svc.untagged_notes() == []


# ── Notes stats / analytics ──────────────────────────────────────────


def test_tag_statistics(svc: NotesService):
    svc.create_note("A", tags=["python", "dev"])
    svc.create_note("B", tags=["python"])
    svc.create_note("C", tags=["dev", "work"])

    stats = svc.tag_statistics()
    stats_dict = dict(stats)
    assert stats_dict["python"] == 2
    assert stats_dict["dev"] == 2
    assert stats_dict["work"] == 1
    # Most popular first
    assert stats[0][1] >= stats[-1][1]


def test_tag_statistics_empty(svc: NotesService):
    svc.create_note("No tags")
    assert svc.tag_statistics() == []
