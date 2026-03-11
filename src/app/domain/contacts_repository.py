from collections import UserDict
from re import fullmatch
from datetime import datetime
import birthdays


class PhoneFormatInvalid(Exception): #custom exception for invalid phone format
    pass


class Field:
    
    def __init__(self, value: object) -> None: #base class for all fields, it just stores the value and returns it as string when needed
        self.value = value


    def __str__(self) -> str:
        return str(self.value)


class Name(Field): #class for name field, it inherits from Field and adds validation to ensure name is not empty or just whitespace
    
    def __init__(self, value: str) -> None:
        super().__init__(value)
        
        if value is None or value.strip() == "": #if the value is None or empty after stripping whitespace, raise ValueError
            raise ValueError("Name cannot be empty.")


class Phone(Field): #class for phone field, inherited from Field, adds validation to ensure phone number is exactly 10 digits
    
    def __init__(self, value: str) -> None:
        super().__init__(value) #store the phone number as a string for easier manipulation later
        
        if fullmatch(r"\d{10}", str(self.value)) is None: #if the value is not 10 digits, raise PhoneFormatInvalid
            raise PhoneFormatInvalid("Phone must be exactly 10 digits (e.g. 0991234567).")


class Birthday(Field): #class for birthday field, it inherits from Field and adds validation to ensure the date is in the correct format and is a valid date
    
    def __init__(self, value: str) -> None:

        if not fullmatch(r"\d{2}\.\d{2}\.\d{4}", value): #if the value does not match the regex for DD.MM.YYYY format, raise ValueError
            raise ValueError("Invalid date format. Use DD.MM.YYYY (e.g. 25.12.1990).")
        
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date() #try to parse the date, if it fails (e.g. 31.02.2020), raise ValueError
        
        except ValueError:
            raise ValueError("Invalid date. Use DD.MM.YYYY (e.g. 25.12.1990).")
        
        super().__init__(birthday) #store the birthday as a date object for easier manipulation later


    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Record: #class for a contact record, it contains a name, a list of phones, and an optional birthday. It has methods to add, remove, edit phones and add a birthday
    
    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None


    def __str__(self) -> str:
        #when converting a Record to string, it will show the name, phones (or "no phones" if there are none), and birthday if it exists
        
        phones_str = '; '.join(p.value for p in self.phones) or "no phones"
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""

        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


    def add_phone(self, phone: str) -> None:
        #add a phone to the record, but only if it is not already in the list of phones. It uses the Phone class to validate the phone number format

        phone = str(phone)

        if phone not in [p.value for p in self.phones]:
            self.phones.append(Phone(phone))


    def remove_phone(self, phone: str) -> bool:
        """remove a phone from the record, it returns True 
        if the phone was found and removed, otherwise it returns False"""
        
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False


    def edit_phone(self, old_phone: str, new_phone: str) -> bool:
        """edit a phone number in the record, it returns True if the old phone was found 
        and replaced with the new phone, otherwise it returns False"""
        
        new_phone_obj = Phone(new_phone)

        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = new_phone_obj
                return True
        return False

   
    def find_phone(self, phone: str) -> Phone | None:
        """find a phone in the record, it returns the Phone object if found, otherwise it returns None"""
        
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    

    def add_birthday(self, value: str) -> None:
        """add a birthday to the record, it uses the Birthday class to validate the date format and value"""

        self.birthday = Birthday(value)


class AddressBook(UserDict): 
    """class for the address book, it inherits from UserDict to store records in a dictionary. 
    It has methods to add a record, find a record by name, delete a record by name, and get upcoming birthdays"""


    def add_record(self, record: Record) -> None:
        #add a record to the address book, it uses the name of the record as the key in the dictionary and the Record object as the value
        
        self.data[record.name.value] = record


    def find(self, name: str) -> Record | None:
        #find a record by name, it returns the Record object if found, otherwise it returns None

        return self.data.get(name)


    def delete(self, name: str) -> Record | None:
        #delete a record by name, it returns the Record object that was removed if found, otherwise it returns None

        return self.data.pop(name, None)


    def get_birthdays(self) -> list[dict[str, str]]: 
        """get upcoming birthdays, it creates a list of users with their names and birthday dates 
        in the required format, then it calls the get_upcoming_birthdays function from the birthdays 
        module to get the list of upcoming birthdays and returns it"""

        users = []

        for record in self.data.values():
            if record.birthday:
                users.append({
                    "name": record.name.value,
                    "birthday": record.birthday.value.strftime("%Y.%m.%d")
                })
        return birthdays.get_upcoming_birthdays(users)