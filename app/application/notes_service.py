from app.domain.models import Note, Tag
from app.domain.repository import NotesRepository


class NotesService:
    """Сервісний шар для нотаток – CRUD через репозиторій."""

    def __init__(self, repository: NotesRepository) -> None:
        self.repository = repository

    def create_note(self, title: str, body: str = "", tags: list[str] | None = None) -> Note:
        Note.validate_title(title)
        if tags:
            for name in tags:
                Tag.validate_name(name)
        note = Note(title=title, body=body)
        if tags:
            return self.repository.add_with_tags(note, tags)
        return self.repository.add(note)

    def get_note(self, note_id: int) -> Note:
        note = self.repository.get_by_id(note_id)
        if note is None:
            raise KeyError(f"Note with id={note_id} not found.")
        return note

    def list_notes(self) -> list[Note]:
        return self.repository.list_all()

    def search_notes(self, query: str) -> list[Note]:
        return self.repository.search(query)

    def update_note(self, note_id: int, title: str | None = None, body: str | None = None) -> Note:
        note = self.get_note(note_id)
        if title is not None:
            note.title = title
        if body is not None:
            note.body = body
        return self.repository.update(note)

    def add_tags(self, note_id: int, tag_names: list[str]) -> Note:
        for name in tag_names:
            Tag.validate_name(name)
        note = self.get_note(note_id)
        return self.repository.add_tags_to_note(note, tag_names)

    def remove_tag(self, note_id: int, tag_name: str) -> Note:
        note = self.get_note(note_id)
        return self.repository.remove_tag_from_note(note, tag_name)

    def delete_note(self, note_id: int) -> None:
        self.repository.delete(note_id)
