from datetime import datetime

from app.domain.models import Contact, Phone
from app.domain.repository import ContactsRepository


class ContactsService:
    def __init__(self, repository: ContactsRepository) -> None:
        self.repository = repository

    def create_contact(self, name: str, phone: str, birthday: str | None = None) -> Contact:
        contact = Contact(name=name)
        contact.phones.append(Phone(value=phone))

        if birthday:
            contact.birthday = datetime.strptime(birthday, "%d.%m.%Y").date()

        return self.repository.add(contact)

    def get_contact(self, contact_id: int) -> Contact:
        contact = self.repository.get_by_id(contact_id)
        if contact is None:
            raise KeyError(f"Contact with id={contact_id} not found.")
        return contact

    def list_contacts(self) -> list[Contact]:
        return self.repository.list_all()

    def search_contacts(self, query: str) -> list[Contact]:
        return self.repository.search(query)

    def add_phone(self, name: str, phone: str) -> Contact:
        results = self.repository.search(name)
        if not results:
            raise KeyError("Contact not found.")

        contact = results[0]
        contact.phones.append(Phone(value=phone))
        return self.repository.update(contact)

    def change_phone(self, name: str, old_phone: str, new_phone: str) -> Contact:
        results = self.repository.search(name)
        if not results:
            raise KeyError("Contact not found.")

        contact = results[0]
        for p in contact.phones:
            if p.value == old_phone:
                p.value = new_phone
                return self.repository.update(contact)

        raise ValueError("Old phone number not found.")

    def set_birthday(self, name: str, birthday_str: str) -> Contact:
        results = self.repository.search(name)
        if not results:
            raise KeyError("Contact not found.")

        try:
            birthday_date = datetime.strptime(birthday_str, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        contact = results[0]
        contact.birthday = birthday_date
        return self.repository.update(contact)

    def delete_contact(self, contact_id: int) -> None:
        self.repository.delete(contact_id)
