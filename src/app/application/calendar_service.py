from app.domain.models import Contact
from app.domain.repository import ContactsRepository


class CalendarService:
    def __init__(self, repository: ContactsRepository) -> None:
        self.repository = repository

    def get_upcoming_birthdays(self, days: int = 7) -> list[Contact]:
        return self.repository.get_upcoming_birthdays(days)
