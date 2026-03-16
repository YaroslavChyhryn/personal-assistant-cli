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


def get_help() -> str:
    return (
        "\nAvailable commands:\n"
        "\nGeneral:"
        "\n  hello                         - Greet the bot"
        "\n  help                          - Show this help message"
        "\n  close / exit                  - Exit the program"
        "\n"
        "\nContacts:"
        "\n  add <name> <phone>            - Add a new contact"
        "\n  change <name> <old> <new>     - Change a contact's phone number"
        "\n  phone <name>                  - Show phone number(s) for a contact"
        "\n  all                           - Show all contacts"
        "\n  add-birthday <name> <date>    - Add birthday to contact"
        "\n  show-birthday <name>          - Show contact birthday"
        "\n  birthdays [days]              - Show upcoming birthdays (default: 7 days)"
        "\n  add-email <name> <email>      - Add email to contact"
        "\n  add-address <name> <address>  - Add address to contact"
        "\n  delete-contact <name>         - Delete a contact"
        "\n"
        "\nNotes:"
        "\n  add-note <title> [body] [#tags...]    - Add a note"
        "\n  list-notes                            - Show all notes"
        "\n  find-note <query>                     - Search notes by text"
        "\n  edit-note <id> <title> [body...]      - Edit a note"
        "\n  delete-note <id>                      - Delete a note"
        "\n  find-tag <tag>                        - Find notes by tag"
        "\n  add-tag <id> <tag1> [tag2...]         - Add tag(s) to a note"
        "\n  remove-tag <id> <tag>                 - Remove a tag from a note"
        "\n  sort-notes                            - Show notes grouped by tag"
        "\n  notes-stats                           - Show notes analytics"
    )


# ── Contacts ──────────────────────────────────────────────────────────


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
        emails = "; ".join(e.value for e in c.emails) if c.emails else "-"
        birthday = c.birthday.strftime("%d.%m.%Y") if c.birthday else "-"
        address = c.address or "-"
        lines.append(
            f"Contact name: {c.name}, phones: {phones}, "
            f"emails: {emails}, birthday: {birthday}, address: {address}"
        )
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
        f"{c.name}: {c.birthday.strftime('%d.%m.%Y')}" for c in upcoming if c.birthday
    )


@input_error
def add_email_cmd(args: list[str], svc: ContactsService) -> str:
    if len(args) < 2:
        raise ValueError("Give me name and email please.")
    name, email, *_ = args
    svc.add_email(name, email)
    return "Email added."


@input_error
def add_address_cmd(args: list[str], svc: ContactsService) -> str:
    if len(args) < 2:
        raise ValueError("Give me name and address please.")
    name = args[0]
    address = " ".join(args[1:])
    svc.set_address(name, address)
    return "Address added."


@input_error
def delete_contact_cmd(args: list[str], svc: ContactsService) -> str:
    if len(args) < 1:
        raise ValueError("Give me contact name please.")
    name, *_ = args
    results = svc.search_contacts(name)
    if not results:
        raise KeyError("Contact not found.")
    contact = results[0]
    assert contact.id is not None
    svc.delete_contact(contact.id)
    return "Contact deleted."


# ── Notes ─────────────────────────────────────────────────────────────


@input_error
def add_note_cmd(args: list[str], svc: NotesService) -> str:
    if len(args) < 1:
        raise ValueError("Give me a title please.")
    title = args[0]
    tags = [w.strip("#") for w in args[1:] if w.startswith("#")]
    body_words = [w for w in args[1:] if not w.startswith("#")]
    body = " ".join(body_words)

    note = svc.create_note(title, body, tags=tags or None)
    return f"Note added with id={note.id}."


@input_error
def list_notes_cmd(svc: NotesService) -> str:
    notes = svc.list_notes()
    if not notes:
        return "No notes saved."
    lines = []
    for n in notes:
        tags = ", ".join(t.name for t in n.tags) if n.tags else "-"
        lines.append(f"[{n.id}] {n.title}: {n.body} (tags: {tags})")
    return "\n".join(lines)


@input_error
def find_note_cmd(args: list[str], svc: NotesService) -> str:
    if len(args) < 1:
        raise ValueError("Give me a search query.")
    query = " ".join(args)
    results = svc.search_notes(query)
    if not results:
        return "No notes found."
    return "\n".join(f"[{n.id}] {n.title}: {n.body}" for n in results)


@input_error
def edit_note_cmd(args: list[str], svc: NotesService) -> str:
    if len(args) < 2:
        raise ValueError("Usage: edit-note <id> <title> [body...]")
    note_id = int(args[0])
    title = args[1]
    body = " ".join(args[2:]) if len(args) > 2 else None
    svc.update_note(note_id, title=title, body=body)
    return "Note updated."


@input_error
def delete_note_cmd(args: list[str], svc: NotesService) -> str:
    if len(args) < 1:
        raise ValueError("Give me a note id.")
    note_id = int(args[0])
    svc.delete_note(note_id)
    return "Note deleted."


@input_error
def find_tag_cmd(args: list[str], svc: NotesService) -> str:
    if len(args) < 1:
        raise ValueError("Give me a tag name.")
    tag = args[0].strip("#")
    results = svc.search_by_tag(tag)
    if not results:
        return f"No notes with tag '{tag}'."
    return "\n".join(f"[{n.id}] {n.title}: {n.body}" for n in results)


@input_error
def add_tag_cmd(args: list[str], svc: NotesService) -> str:
    if len(args) < 2:
        raise ValueError("Give me note id and tag name(s). Usage: add-tag <id> <tag1> [tag2...]")
    note_id = int(args[0])
    tag_names = [t.strip("#") for t in args[1:]]
    svc.add_tags(note_id, tag_names)
    return "Tag(s) added."


@input_error
def sort_notes_cmd(svc: NotesService) -> str:
    grouped = svc.notes_grouped_by_tag()
    untagged = svc.untagged_notes()

    if not grouped and not untagged:
        return "No notes saved."

    lines: list[str] = []
    for tag_name, notes in grouped.items():
        lines.append(f"\n[#{tag_name}]")
        for n in notes:
            lines.append(f"  [{n.id}] {n.title}: {n.body}")

    if untagged:
        lines.append("\n[no tags]")
        for n in untagged:
            lines.append(f"  [{n.id}] {n.title}: {n.body}")

    return "\n".join(lines)


@input_error
def notes_stats_cmd(svc: NotesService) -> str:
    all_notes = svc.list_notes()
    if not all_notes:
        return "No notes saved."

    total = len(all_notes)
    tag_counts = svc.tag_statistics()
    untagged = svc.untagged_notes()

    lines = [f"Total notes: {total}"]

    if tag_counts:
        lines.append(f"Total tags used: {len(tag_counts)}")
        lines.append("\nTag usage (most popular first):")
        for tag_name, count in tag_counts:
            bar = "█" * count
            lines.append(f"  #{tag_name}: {count} note(s) {bar}")
    else:
        lines.append("No tags used.")

    if untagged:
        lines.append(f"\nNotes without tags: {len(untagged)}")
        for n in untagged:
            lines.append(f"  [{n.id}] {n.title}")

    return "\n".join(lines)


@input_error
def remove_tag_cmd(args: list[str], svc: NotesService) -> str:
    if len(args) < 2:
        raise ValueError("Give me note id and tag name. Usage: remove-tag <id> <tag>")
    note_id = int(args[0])
    tag_name = args[1].strip("#")
    svc.remove_tag(note_id, tag_name)
    return "Tag removed."


# ── Main loop ─────────────────────────────────────────────────────────


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
            elif command == "help":
                print(get_help())
            # Contacts
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
            elif command == "add-email":
                print(add_email_cmd(args, contacts_svc))
            elif command == "add-address":
                print(add_address_cmd(args, contacts_svc))
            elif command == "delete-contact":
                print(delete_contact_cmd(args, contacts_svc))
            # Notes
            elif command == "add-note":
                print(add_note_cmd(args, notes_svc))
            elif command == "list-notes":
                print(list_notes_cmd(notes_svc))
            elif command == "find-note":
                print(find_note_cmd(args, notes_svc))
            elif command == "edit-note":
                print(edit_note_cmd(args, notes_svc))
            elif command == "delete-note":
                print(delete_note_cmd(args, notes_svc))
            elif command == "find-tag":
                print(find_tag_cmd(args, notes_svc))
            elif command == "add-tag":
                print(add_tag_cmd(args, notes_svc))
            elif command == "remove-tag":
                print(remove_tag_cmd(args, notes_svc))
            elif command == "sort-notes":
                print(sort_notes_cmd(notes_svc))
            elif command == "notes-stats":
                print(notes_stats_cmd(notes_svc))
            else:
                print("Invalid command.")
