from datetime import date, timedelta
from unittest.mock import patch

import pytest

from app.application.calendar_service import CalendarService
from app.application.contacts_service import ContactsService
from app.domain.repository import BaseRepository, ContactsRepository


def test_upcoming_birthdays(contacts_repo: ContactsRepository):
    svc = ContactsService(contacts_repo)
    cal = CalendarService(contacts_repo)

    today = date.today()
    upcoming = today + timedelta(days=3)
    birthday_str = upcoming.strftime("%d.%m.%Y")

    svc.create_contact("Alice", "1234567890", birthday=birthday_str)

    results = cal.get_upcoming_birthdays(days=7)
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_no_upcoming_birthdays(contacts_repo: ContactsRepository):
    svc = ContactsService(contacts_repo)
    cal = CalendarService(contacts_repo)

    svc.create_contact("Alice", "1234567890", birthday="01.01.2000")

    with patch("app.domain.repository.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 15)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        results = cal.get_upcoming_birthdays(days=7)
    assert results == []


def test_birthday_without_date(contacts_repo: ContactsRepository):
    svc = ContactsService(contacts_repo)
    cal = CalendarService(contacts_repo)

    svc.create_contact("Bob", "0987654321")

    results = cal.get_upcoming_birthdays(days=7)
    assert results == []


def test_birthday_on_saturday_moves_to_monday(contacts_repo: ContactsRepository):
    svc = ContactsService(contacts_repo)
    cal = CalendarService(contacts_repo)

    # Find the next Saturday from today
    today = date.today()
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    saturday = today + timedelta(days=days_until_saturday)
    birthday_str = saturday.strftime("%d.%m.%Y")

    svc.create_contact("Sat", "1234567890", birthday=birthday_str)

    # The congratulation moves to Monday (+2), so we need enough range
    results = cal.get_upcoming_birthdays(days=days_until_saturday + 2)
    assert len(results) == 1
    assert results[0].name == "Sat"


def test_birthday_on_sunday_moves_to_monday(contacts_repo: ContactsRepository):
    svc = ContactsService(contacts_repo)
    cal = CalendarService(contacts_repo)

    # Find the next Sunday from today
    today = date.today()
    days_until_sunday = (6 - today.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7
    sunday = today + timedelta(days=days_until_sunday)
    birthday_str = sunday.strftime("%d.%m.%Y")

    svc.create_contact("Sun", "1234567890", birthday=birthday_str)

    # The congratulation moves to Monday (+1), so we need enough range
    results = cal.get_upcoming_birthdays(days=days_until_sunday + 1)
    assert len(results) == 1
    assert results[0].name == "Sun"


def test_base_repository_search_not_implemented(session):
    class DummyRepo(BaseRepository):
        model = None

    repo = DummyRepo(session)
    with pytest.raises(NotImplementedError):
        repo.search("test")
