from sqlmodel import Session

from app.application.calendar_service import CalendarService
from app.application.contacts_service import ContactsService
from app.application.notes_service import NotesService
from app.db import engine
from app.domain.repository import ContactsRepository, NotesRepository


def parse_input(user_input: str) -> tuple[str, list[str]]:
    cmd, *args = user_input.strip().split()
    return cmd.lower(), args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return e.args[0] if e.args else "Contact not found."
        except ValueError as e:
            return e.args[0] if e.args else "Invalid input."
        except IndexError as e:
            return e.args[0] if e.args else "Not enough arguments."

    return inner


@input_error
def add_contact(args: list[str], svc: ContactsService) -> str:
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")
    name, phone, *_ = args
    svc.create_contact(name, phone)
    return "Contact added."


@input_error
def change_contact(args: list[str], svc: ContactsService) -> str:
    if len(args) < 3:
        raise ValueError("Give me name, old phone and new phone please.")
    name, old_phone, new_phone, *_ = args
    svc.change_phone(name, old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: list[str], svc: ContactsService) -> str:
    if len(args) < 1:
        raise ValueError("Enter user name.")
    name, *_ = args

    results = svc.search_contacts(name)
    if not results:
        raise KeyError("Contact not found.")

    phones = results[0].phones
    if not phones:
        return "No phones found for this contact."
    return "; ".join(p.value for p in phones)


@input_error
def show_all(svc: ContactsService) -> str:
    contacts = svc.list_contacts()
    if not contacts:
        return "No contacts saved."

    lines = []
    for c in contacts:
        phones = "; ".join(p.value for p in c.phones) if c.phones else "-"
        birthday = c.birthday.strftime("%d.%m.%Y") if c.birthday else "-"
        lines.append(f"Contact name: {c.name}, phones: {phones}, birthday: {birthday}")
    return "\n".join(lines)


@input_error
def add_birthday_cmd(args: list[str], svc: ContactsService) -> str:
    if len(args) < 2:
        raise ValueError("Give me name and birthday please.")
    name, birthday_str, *_ = args
    svc.set_birthday(name, birthday_str)
    return "Birthday added."


@input_error
def show_birthday_cmd(args: list[str], svc: ContactsService) -> str:
    if len(args) < 1:
        raise ValueError("Enter user name.")
    name, *_ = args

    results = svc.search_contacts(name)
    if not results:
        raise KeyError("Contact not found.")

    contact = results[0]
    if contact.birthday is None:
        return "Birthday is not set for this contact."
    return contact.birthday.strftime("%d.%m.%Y")


@input_error
def birthdays_cmd(args: list[str], svc: CalendarService) -> str:
    days = int(args[0]) if args else 7
    upcoming = svc.get_upcoming_birthdays(days)
    if not upcoming:
        return f"No upcoming birthdays in the next {days} days."
    return "\n".join(
        f"{c.name}: {c.birthday.strftime('%d.%m.%Y')}" for c in upcoming if c.birthday is not None
    )


@input_error
def add_note(args: list[str], svc: NotesService) -> str:
    if len(args) < 1:
        raise ValueError("Give me a title please.")
    title = args[0]
    body_words = [w for w in args[1:] if not w.startswith("#")]
    body = " ".join(body_words)

    note = svc.create_note(title, body)
    return f"Note added with id={note.id}."


@input_error
def find_note(args: list[str], svc: NotesService) -> str:
    if len(args) < 1:
        raise ValueError("Give me a search query.")
    query = " ".join(args)
    results = svc.search_notes(query)
    if not results:
        return "No notes found."
    return "\n".join(f"[{n.id}] {n.title}: {n.body}" for n in results)


@input_error
def find_tag(args: list[str], repo: NotesRepository) -> str:
    if len(args) < 1:
        raise ValueError("Give me a tag name.")
    tag = args[0].strip("#")
    results = repo.search_by_tag(tag)
    if not results:
        return f"No notes with tag '{tag}'."
    return "\n".join(f"[{n.id}] {n.title}: {n.body}" for n in results)


def run() -> None:
    print("Welcome to the assistant bot!")

    with Session(engine) as session:
        contacts_repo = ContactsRepository(session)
        notes_repo = NotesRepository(session)

        contacts_svc = ContactsService(contacts_repo)
        notes_svc = NotesService(notes_repo)
        calendar_svc = CalendarService(contacts_repo)

        while True:
            user_input = input("Enter a command: ")

            if not user_input.strip():
                continue

            command, args = parse_input(user_input)

            if command in ("close", "exit"):
                print("Good bye!")
                break
            elif command == "hello":
                print("How can I help you?")
            elif command == "add":
                print(add_contact(args, contacts_svc))
            elif command == "change":
                print(change_contact(args, contacts_svc))
            elif command == "phone":
                print(show_phone(args, contacts_svc))
            elif command == "all":
                print(show_all(contacts_svc))
            elif command == "add-birthday":
                print(add_birthday_cmd(args, contacts_svc))
            elif command == "show-birthday":
                print(show_birthday_cmd(args, contacts_svc))
            elif command == "birthdays":
                print(birthdays_cmd(args, calendar_svc))
            elif command == "add-note":
                print(add_note(args, notes_svc))
            elif command == "find-note":
                print(find_note(args, notes_svc))
            elif command == "find-tag":
                print(find_tag(args, notes_repo))
            else:
                print("Invalid command.")
