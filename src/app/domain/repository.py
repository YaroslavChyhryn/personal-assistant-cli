from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """Base repository with working CRUD operations.

    Subclasses only need to set `model` and add domain-specific queries.

    Usage:
        class ContactsRepository(BaseRepository[Contact]):
            model = Contact

            def get_upcoming_birthdays(self, days: int = 7) -> list[Contact]: ...
    """

    model: type[T]

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> T | None:
        return self.session.get(self.model, entity_id)

    def list_all(self) -> list[T]:
        return list(self.session.exec(select(self.model)).all())

    def search(self, query: str) -> list[T]:
        raise NotImplementedError("Override search() in subclass")

    def update(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> None:
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()


# TODO (Dev 1):
#
# class ContactsRepository(BaseRepository[Contact]):
#     model = Contact
#     def search(self, query: str) -> list[Contact]: ...
#     def get_upcoming_birthdays(self, days: int = 7) -> list[Contact]: ...

# TODO (Dev 2):
#
# class NotesRepository(BaseRepository[Note]):
#     model = Note
#     def search(self, query: str) -> list[Note]: ...
#     def search_by_tag(self, tag: str) -> list[Note]: ...
#     def add_with_tags(self, note: Note, tag_names: list[str]) -> Note: ...
