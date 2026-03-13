import pytest

from app.application.contacts_service import ContactsService
from app.domain.repository import ContactsRepository


@pytest.fixture
def svc(contacts_repo: ContactsRepository) -> ContactsService:
    return ContactsService(contacts_repo)


def test_create_contact(svc: ContactsService):
    contact = svc.create_contact("Alice", "1234567890")
    assert contact.id is not None
    assert contact.name == "Alice"
    assert len(contact.phones) == 1
    assert contact.phones[0].value == "1234567890"


def test_create_contact_with_birthday(svc: ContactsService):
    contact = svc.create_contact("Bob", "0987654321", birthday="15.06.1990")
    assert contact.birthday is not None
    assert contact.birthday.day == 15
    assert contact.birthday.month == 6
    assert contact.birthday.year == 1990


def test_get_contact(svc: ContactsService):
    created = svc.create_contact("Alice", "1234567890")
    assert created.id is not None
    found = svc.get_contact(created.id)
    assert found.name == "Alice"


def test_get_contact_not_found(svc: ContactsService):
    with pytest.raises(KeyError):
        svc.get_contact(999)


def test_list_contacts(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    svc.create_contact("Bob", "0987654321")
    contacts = svc.list_contacts()
    assert len(contacts) == 2


def test_search_contacts(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    svc.create_contact("Bob", "0987654321")
    results = svc.search_contacts("Ali")
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_add_phone(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    updated = svc.add_phone("Alice", "1111111111")
    assert len(updated.phones) == 2


def test_add_phone_not_found(svc: ContactsService):
    with pytest.raises(KeyError):
        svc.add_phone("Nobody", "1234567890")


def test_change_phone(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    updated = svc.change_phone("Alice", "1234567890", "9999999999")
    assert updated.phones[0].value == "9999999999"


def test_change_phone_old_not_found(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    with pytest.raises(ValueError, match="Old phone number not found"):
        svc.change_phone("Alice", "0000000000", "9999999999")


def test_set_birthday(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    updated = svc.set_birthday("Alice", "25.12.2000")
    assert updated.birthday is not None
    assert updated.birthday.day == 25
    assert updated.birthday.month == 12


def test_set_birthday_invalid_format(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    with pytest.raises(ValueError, match="Invalid date format"):
        svc.set_birthday("Alice", "not-a-date")


def test_delete_contact(svc: ContactsService):
    created = svc.create_contact("Alice", "1234567890")
    assert created.id is not None
    svc.delete_contact(created.id)
    assert svc.list_contacts() == []


def test_change_phone_contact_not_found(svc: ContactsService):
    with pytest.raises(KeyError, match="Contact not found"):
        svc.change_phone("Nobody", "1234567890", "9999999999")


def test_set_birthday_contact_not_found(svc: ContactsService):
    with pytest.raises(KeyError, match="Contact not found"):
        svc.set_birthday("Nobody", "25.12.2000")


def test_add_email(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    updated = svc.add_email("Alice", "alice@example.com")
    assert len(updated.emails) == 1
    assert updated.emails[0].value == "alice@example.com"


def test_add_email_not_found(svc: ContactsService):
    with pytest.raises(KeyError, match="Contact not found"):
        svc.add_email("Nobody", "nobody@example.com")


def test_set_address(svc: ContactsService):
    svc.create_contact("Alice", "1234567890")
    updated = svc.set_address("Alice", "123 Main St")
    assert updated.address == "123 Main St"


def test_set_address_not_found(svc: ContactsService):
    with pytest.raises(KeyError, match="Contact not found"):
        svc.set_address("Nobody", "123 Main St")


def test_phone_validation_rejects_short():
    from app.domain.models import Phone

    with pytest.raises(ValueError, match="10 digits"):
        Phone.model_validate({"value": "123", "contact_id": 1})


def test_phone_validation_accepts_valid():
    from app.domain.models import Phone

    phone = Phone.model_validate({"value": "1234567890", "contact_id": 1})
    assert phone.value == "1234567890"


def test_email_validation_rejects_invalid():
    from app.domain.models import Email

    with pytest.raises(ValueError, match="Invalid email"):
        Email.model_validate({"value": "not-an-email", "contact_id": 1})


def test_email_validation_accepts_valid():
    from app.domain.models import Email

    email = Email.model_validate({"value": "test@example.com", "contact_id": 1})
    assert email.value == "test@example.com"
