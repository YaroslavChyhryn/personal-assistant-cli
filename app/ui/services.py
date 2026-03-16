from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

import streamlit as st
from sqlmodel import Session

from app.application.calendar_service import CalendarService
from app.application.contacts_service import ContactsService
from app.application.notes_service import NotesService
from app.bootstrap import bootstrap
from app.db import engine
from app.domain.repository import ContactsRepository, NotesRepository


@st.cache_resource
def setup() -> None:
    bootstrap()


@contextmanager
def get_services() -> (
    Generator[
        tuple[ContactsService, NotesService, CalendarService],
        None,
        None,
    ]
):
    with Session(engine) as session:
        contacts_repo = ContactsRepository(session)
        notes_repo = NotesRepository(session)
        yield (
            ContactsService(contacts_repo),
            NotesService(notes_repo),
            CalendarService(contacts_repo),
        )
