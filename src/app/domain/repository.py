from datetime import date, timedelta
from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, or_, select

from app.domain.models import Contact, Note, NoteTagLink, Tag

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


class ContactsRepository(BaseRepository[Contact]):
    # BaseRepository will use this model for generic CRUD operations
    model = Contact

    def search(self, query: str) -> list[Contact]:
        # Search contacts by partial name match
        statement = select(Contact).where(Contact.name.contains(query))
        return list(self.session.exec(statement).all())

    def get_upcoming_birthdays(self, days: int = 7) -> list[Contact]:
        # 1. take birthday
        # 2. move it to current year
        # 3. if already passed -> next year
        # 4. if Saturday/Sunday -> move congratulation date to Monday
        # 5. include contact if congratulation date is in range [today, today + days]
        today = date.today()
        end_date = today + timedelta(days=days)
        result: list[Contact] = []

        for contact in self.list_all():
            if contact.birthday is None:
                continue

            # Build this year's birthday date
            birthday_date = contact.birthday.replace(year=today.year)

            # If birthday already passed this year, use next year
            if birthday_date < today:
                birthday_date = birthday_date.replace(year=today.year + 1)

            # Move weekend congratulations to Monday
            congratulation_date = birthday_date
            if congratulation_date.weekday() == 5:  # Saturday
                congratulation_date = congratulation_date + timedelta(days=2)
            elif congratulation_date.weekday() == 6:  # Sunday
                congratulation_date = congratulation_date + timedelta(days=1)

            if today <= congratulation_date <= end_date:
                result.append(contact)

        return result


class NotesRepository(BaseRepository[Note]):
    model = Note

    def search(self, query: str) -> list[Note]:
        statement = select(Note).where(
            or_(
                Note.title.contains(query),
                Note.body.contains(query),
            )
        )
        return list(self.session.exec(statement).all())

    def search_by_tag(self, tag: str) -> list[Note]:
        statement = select(Note).join(NoteTagLink).join(Tag).where(Tag.name == tag)
        return list(self.session.exec(statement).all())

    def add_with_tags(self, note: Note, tag_names: list[str]) -> Note:
        for name in tag_names:
            statement = select(Tag).where(Tag.name == name)
            tag = self.session.exec(statement).first()
            if tag is None:
                tag = Tag(name=name)
            note.tags.append(tag)

        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note
