# TODO: implement ContactsService (CRUD + validation via repository)

from typing import Callable
from domain import AddressBook, Record, PhoneFormatInvalid
from domain.common.validators import input_error


def parse_input(user_input: str) -> tuple[str, list]: #parse user input, it splits the input into command and arguments, and returns them as a tuple
    cmd, *args = user_input.strip().split()
    cmd = cmd.strip().lower()
    return cmd, args


def get_help() -> str: #return a string with the help text for the user, it lists all available commands and their descriptions
    return (
        "\n  add <name> <phone>                    - Add contact or new phone"
        "\n  change <name> <old_phone> <new_phone> - Update a phone number"
        "\n  phone <name>                          - Show phone(s) for a contact"
        "\n  all                                   - Show all contacts"
        "\n  add-birthday <name> <DD.MM.YYYY>      - Add a birthday"
        "\n  show-birthday <name>                  - Show a birthday"
        "\n  birthdays                             - Upcoming birthdays this week"
        "\n  hello                                 - Greeting"
        "\n  close / exit                          - Quit"
    )


@input_error
def add_contact(args, book: AddressBook) -> str: 
    """add a contact or a new phone number to an existing contact"""

    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None: #if the contact does not exist, create a new record and add it to the address book, otherwise use the existing record
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone: #if a phone number is provided, add it to the record using the add_phone method, which will validate the phone number format
        record.add_phone(phone)

    return message


@input_error
def change_contact(args, book: AddressBook) -> str:
    """change a phone number for an existing contact, it takes the arguments and the address book as input"""

    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if not record: #if the contact is not found in the address book, raise a KeyError to be handled by the input_error decorator
        raise KeyError
    
    if record.edit_phone(old_phone, new_phone): #if the old phone number is found and replaced with the new phone number, return a success message
        return f"Phone updated for '{name}': {old_phone} -> {new_phone}."
    
    return f"Phone {old_phone} not found for '{name}'. Use 'phone {name}' to see saved numbers." #if the old phone number is not found in the record, return a message 

@input_error
def show_phone(args, book: AddressBook) -> str:
    """show phone numbers for a contact, it takes the arguments and the address book as input"""
    
    name, *_ = args
    record = book.find(name)
    
    if not record:
        raise KeyError
    
    if not record.phones:
        return f"'{name}' has no phone numbers saved."
    
    return f"{name}: {'; '.join(p.value for p in record.phones)}"


def show_all(book: AddressBook) -> str:
    """show all contacts in the address book, it takes the address book as input 
    and returns a formatted string with all contacts and their details"""
    
    if not book.data:
        return "No contacts saved yet. Use 'add <name> <phone>' to add one."
    
    lines: list[str] = ["All contacts:"]
    
    for record in book.data.values():
        lines.append(f"  {record}")
    
    return "\n".join(lines)


@input_error
def add_birthday(args, book: AddressBook) -> str:
    """add a birthday to a contact, it takes the arguments and the address book as input"""

    name, birthday, *_ = args
    record = book.find(name)
    
    if not record:
        raise KeyError
    
    record.add_birthday(birthday) #add a birthday to the record using the add_birthday method, which will validate the date format and value
    
    return f"Birthday {birthday} saved for '{name}'."


@input_error
def show_birthday(args, book: AddressBook) -> str: 
    """show a birthday for a contact, it takes the arguments and the address book as input"""

    name, *_ = args
    record = book.find(name)
    
    if not record:
        raise KeyError
    
    if not record.birthday:
        return f"'{name}' has no birthday saved. Use 'add-birthday {name} DD.MM.YYYY'."
    
    return f"{name}'s birthday: {record.birthday}"


@input_error
def birthdays(args, book: AddressBook) -> str:
    """show upcoming birthdays for the next 7 days, it takes the arguments and the address book as input, 
    it uses the get_birthdays method of the address book to get a list of upcoming birthdays and formats it into a string for display"""
    
    upcoming = book.get_birthdays() #call the get_birthdays method of the address book to get a list of upcoming birthdays
    
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    
    lines = ["Upcoming birthdays:"]
    
    for u in upcoming: #
        lines.append(f"  {u['name']}: congratulate on {u['congratulation_date']}") 
    
    return "\n".join(lines) #join the lines into a single string with newlines for display