from app.domain.models import Note
from app.domain.repository import NotesRepository


class NotesService:
    """Сервісний шар для нотаток – CRUD через репозиторій."""

    def __init__(self, repository: NotesRepository) -> None:
        self.repository = repository

    def create_note(self, title: str, body: str = "") -> Note:
        return self.repository.add(Note(title=title, body=body))

    def get_note(self, note_id: int) -> Note:
        note = self.repository.get_by_id(note_id)
        if note is None:
            raise KeyError(f"Note with id={note_id} not found.")
        return note

    def list_notes(self) -> list[Note]:
        return self.repository.list_all()

    def search_notes(self, query: str) -> list[Note]:
        return self.repository.search(query)

    def delete_note(self, note_id: int) -> None:
        self.repository.delete(note_id)
