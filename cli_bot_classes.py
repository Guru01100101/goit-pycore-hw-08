from collections import UserDict
from datetime import date, timedelta
from typing import List
from normalize_phone import normalize_phone


class Field:
    """Base class for representing fields with a name and value.

    Attributes:
        name (str): The name of the field.
        value (str): The value of the field.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        """Return a string representation of the field."""
        return f'{self.name}: {self.value}'


class Name(Field):
    """Class for representing a name field.

    Inherits from Field.

    Attributes:
        name (str): The name oj contact.
    """

    def __init__(self, name):
        super().__init__('Name', name)


class Phone(Field):
    """Class for representing a phone field.

    Inherits from Field.

    Attributes:
        phone (str): The phone number of the contact.

    Before storing the phone number, it is normalized using the normalize_phone function from previous HW.
    """

    def __init__(self, phone):
        super().__init__('Phone', normalize_phone(phone))


class Birthday(Field):
    def __init__(self, value: str):
        super().__init__('Birthday', value)
        try:
            day, month, year = map(int, value.split('.'))
            self.value = date(year, month, day)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    """Class for representing a contact record with a name and a list of phones.

    Attributes:
        name (Name): The name of the contact. (required)
        phones (List[Phone]): A list of phone numbers of the contact. (optional)
        birthday (Birthday): The birthday of the contact. (optional)

    """

    def __init__(self, name, phones: List[str] = None, birthday: Birthday = None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if phones is not None:
            for phone in phones:
                try:
                    self.add_phone(phone)
                except ValueError as e:
                    print(e)
        if birthday:
            self.add_birthday(birthday)

    def add_phone(self, phone):
        """Add a phone number to the contact.

        Args:
            phone (str): The phone number to add.

        Raises:
            ValueError: If the phone number already exists in the contact.
            ValueError (from normalize_phone): If the phone number is not valid.
        """
        if phone in [p.value for p in self.phones]:
            raise ValueError(f"Phone {phone} already exists")
        self.phones.append(Phone(phone))

    def edit_phone(self, phone, new_phone):
        """Edit an existing phone number in the contact.

        Args:
            phone (str): The phone number to edit.
            new_phone (str): The new phone number to replace the old one.

        Returns:
            str: A message indicating the phone number was edited.
        """
        for p in self.phones:
            if p.value == normalize_phone(phone):
                p.value = normalize_phone(new_phone)
                return f"Phone {phone} edited to {new_phone}"

    def search_phone(self, phone):
        """Search for a phone number in the record.

        Args:
            phone (str): The phone number to search for.

        Returns:
            Phone: The phone object if found, None otherwise.
        """
        for p in self.phones:
            if p.value == normalize_phone(phone):
                return p
        return None

    def delete_phone(self, phone):
        """Delete a phone number from the record.

        Args:
            phone (str): The phone number to delete.

        Returns:
            str: A message indicating the phone number was deleted.
        """
        for p in self.phones:
            if p.value == normalize_phone(phone):
                self.phones.remove(p)
                return f"Phone {phone} deleted"

    def add_birthday(self, value):
        try:
            self.birthday = Birthday(value)
        except ValueError as e:
            print(e)

    def __str__(self):
        """Return a string representation of the contact record."""
        return (f"Contact name: {self.name.value}, "
                f"phones: {'; '.join(p.value for p in self.phones)}")


class AddressBook(UserDict):
    """Class for representing an address book with a dictionary of contact records.

    Inherits from UserDict.

    Methods:
        add_record: Add a contact record to the address book.
        find: Find a contact record by name. (in future may be by phone number)
        delete_record: Delete a contact record by name.
    """

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        """Find a contact record by name.

        Args:
            name (str): The name of the contact to find.

        Returns:
            Record: The contact record if found, None otherwise.
        """
        return self.data.get(name)

    def delete_record(self, name):
        """Delete a contact record by name.

        Args:
            name (str): The name of the contact to delete.
        """
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming_birthdays = []
        for record in self.data.values():
            birthday_this_year = date(today.year, record.birthday.value.month, record.birthday.value.day)
            days_until_birthday = (birthday_this_year - today).days
            if birthday_this_year.weekday() == 5:
                days_until_birthday += 2
            elif birthday_this_year.weekday() == 6:
                days_until_birthday += 1
            if 0 <= days_until_birthday <= 7:
                congrats_day = date.today() + timedelta(days=days_until_birthday)
                upcoming_birthdays.append((record.name.value, birthday_this_year, congrats_day))
        return f"Upcoming birthdays: {'\n'.join(f'{name} on {birthday}' for name, birthday, congrats_day in upcoming_birthdays)}"

    def __str__(self):
        """Return a string representation of the address book."""
        return '\n'.join(str(record) for record in self.data.values())
