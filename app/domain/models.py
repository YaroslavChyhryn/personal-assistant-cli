import re
from datetime import date

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

# ── Contacts (Dev 1) ────────────────────────────────────────────────


class Email(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    value: str
    contact_id: int = Field(foreign_key="contact.id")
    contact: "Contact" = Relationship(back_populates="emails")

    @field_validator("value")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v


class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str | None = None
    birthday: date | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Contact name cannot be empty")
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Address cannot be empty if provided")
        return v

    phones: list["Phone"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    emails: list["Email"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Phone(SQLModel, table=True):
    # Primary key for phone row
    id: int | None = Field(default=None, primary_key=True)

    # Phone number value
    value: str

    # Foreign key to contact table
    contact_id: int = Field(foreign_key="contact.id")

    # Back reference to owning contact
    contact: Contact = Relationship(back_populates="phones")

    @field_validator("value")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Keep original homework validation:
        # phone must contain exactly 10 digits
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone must contain exactly 10 digits")
        return v


# ── Notes + Tags (Dev 2) ────────────────────────────────────────────


class NoteTagLink(SQLModel, table=True):
    """Link-таблиця для зв'язку many-to-many між Note і Tag."""

    note_id: int = Field(foreign_key="note.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    """Тег для нотаток. Ім'я унікальне."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    notes: list["Note"] = Relationship(back_populates="tags", link_model=NoteTagLink)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tag name cannot be empty")
        return v.strip()


class Note(SQLModel, table=True):
    """Нотатка з заголовком, тілом та тегами."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    body: str = ""

    tags: list[Tag] = Relationship(back_populates="notes", link_model=NoteTagLink)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Note title cannot be empty")
        return v.strip()
