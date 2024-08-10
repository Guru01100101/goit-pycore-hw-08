import json
from functools import wraps
from pathlib import Path
from typing import List, Dict

from cli_bot_classes import AddressBook, Record
from normalize_phone import normalize_phone

PHONEBOOK_FILE = "phonebook.json"


def load_phonebook(filename=PHONEBOOK_FILE) -> AddressBook:
    """Function to load the phonebook from the file.

    __args__:
        Filename: str
    __return__:
        AddressBook object
    """
    path = Path(filename)
    try:
        with open(path, "r") as file:
            return AddressBook(json.load(file))
    except FileNotFoundError:
        return AddressBook()


def save_phonebook(phonebook: AddressBook, filename=PHONEBOOK_FILE) -> None:
    """Function to save the phonebook to the file.

    __args__:
        phonebook: AddressBook object
        filename: str
            The path to the file to save the phonebook. Default is PHONEBOOK_FILE.
    __return__:
        None
    """
    path = Path(filename)
    with open(path, "w") as file:
        json.dump(phonebook, file, indent=4)


def input_error(func):
    """
    Decorator to handle input errors in the bot. Handles the input error and prints the error message.
    __errors__:
        - KeyError:
        - ValueError:
        - IndexError:
    __return__: str
        The error message
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return str(e)
        except ValueError as e:
            return str(e)
        except IndexError as e:
            return "Invalid command.\nAvailable commands:\nhello, add, change, delete, search, show, close, exit"

    return wrapper


@input_error
def add_contact(
        name: str,
        phonebook: AddressBook,
        phone: str = None,
        birthday: str = None
) -> None:
    """Function to add a contact to the phonebook.

    __args__:
        name: str
            The name of the contact
        phonebook: AddressBook object
            The phonebook dictionary
        phone: str
            The phone number of the contact. Not required.
        birthday: str
            The birthday of the contact. Not required.
    __return__:
        None
    """
    record = phonebook.find(name)
    if record:
        # add phone to existing record
        record.add_phone(phone)
        if birthday:
            record.add_birthday(birthday)
        print(f"Phone number {phone} added to contact {name}")
    else:
        # create new record
        record = Record(name)
        record.add_phone(phone)
        if birthday:
            record.add_birthday(birthday)
        phonebook.add_record(record)
        print(f"Contact {name} added with phone number {phone}")


@input_error
def change_contact(name: str, new_phone: str, phonebook: AddressBook) -> None:
    """Function to change the phone number of a contact.

    __args__:
        name: str
            The name of the contact
        new_phone: str
            The new phone number of the contact
        phonebook: dict
            The phonebook dictionary
    __return__:
        None
    """
    record = phonebook.get(name)
    if not record:
        raise ValueError(f"Contact {name} not found.")

    new_phone = normalize_phone(new_phone)
    record.edit_phone(record.phones[0].value, new_phone)
    print(f"Contact {name} updated.\nNew phone: {new_phone}")


@input_error
def delete_contact(name: str, phonebook: AddressBook) -> None:
    """Function to delete a contact from the phonebook.

    __args__:
        name: str
            The name of the contact
        phonebook: dict
            The phonebook dictionary
    __return__:
        None
    """
    if not phonebook.find(name):
        raise ValueError(f"Contact {name} not found.")
    phonebook.delete_record(name)
    print(f"Contact {name} deleted.")


@input_error
def search_contact(pattern: str, phonebook: AddressBook) -> None:
    """Function to search for a contact in the phonebook.

    __args__:
        pattern: str
            The search pattern
        phonebook: dict
            The phonebook dictionary
    __return__:
        None
    """

    found = False

    for name, record in phonebook.items():
        if pattern.lower() in name.lower() or any(pattern.lower() in phone.value.lower() for phone in record.phones):
            print(f"{name}: {'; '.join(phone.value for phone in record.phones)}")
            found = True

    if not found:
        raise ValueError(f"Contact {pattern} not found.")


@input_error
def show_phonebook(phonebook: AddressBook, sorted_=True) -> None:
    """Function to pint the phonebook to console.

    __args__:
        phonebook: dict
            The phonebook dictionary
        sorted_: bool
            Flag to sort the phonebook by name. Default is True.
    __return__:
        None
    """
    records = list(phonebook.values())
    if sorted_:  # Sort the phonebook by name
        records.sort(key=lambda x: x.name.value)
    for contact in records:
        print(contact)


@input_error
def add_birthday(name: str, birthday: str, phonebook: AddressBook) -> None:
    """Function to add a birthday to a contact.

    __args__:
        name: str
            The name of the contact
        birthday: str
            The birthday to add
        phonebook: AddressBook
            The phonebook object
    __return__:
        None
    """
    record = phonebook.find(name)
    if not record:
        raise ValueError(f"Contact {name} not found.")

    record.add_birthday(birthday)
    print(f"Birthday for contact {name} added: {birthday}")


@input_error
def show_birthday(name: str, phonebook: AddressBook) -> None:
    """Function to show the birthday of a contact.

    __args__:
        name: str
            The name of the contact
        phonebook: AddressBook
            The phonebook object
    __return__:
            None
    """
    record = phonebook.find(name)
    if not record:
        raise ValueError(f"Contact {name} not found.")

    if record.birthday:
        print(f"Birthday for contact {name}: {record.birthday.value.strftime('%A, %B %d')}")
    else:
        print(f"No birthday found for contact {name}")


@input_error
def birthdays(phonebook: AddressBook) -> None:
    """Function to show contacts to congratulate in the next week.

    __args__:
        phonebook: AddressBook
            The phonebook object
    __return__:
        None
    """
    upcoming_birthdays = phonebook.get_upcoming_birthdays()
    if not upcoming_birthdays:
        print("No upcoming birthdays in the next week.")

    print("Upcoming birthdays in the next week:")
    for name, birthday, congrats_day in upcoming_birthdays:
        print(f"{name} on {birthday.strftime('%A, %B %d')} (congratulate on {congrats_day.strftime('%A, %B %d')})")


def main(phonebook=None):
    print("Welcome to the assistant bot!")

    if phonebook is None:  # Load the phonebook if not provided
        phonebook = load_phonebook()

    commands = {
        "hello": lambda _: print("How can I help you?"),
        "add": lambda args: add_contact(args[0], phonebook, phone=args[1]),
        "change": lambda args: change_contact(args[0], args[1], phonebook),
        "delete": lambda args: delete_contact(args[0], phonebook),
        "search": lambda args: search_contact(args[0], phonebook),
        "show": lambda args: show_phonebook(phonebook, sorted_=False),
        "all": lambda args: show_phonebook(phonebook, sorted_=False),
        "close": lambda _: print("Good bye!"),
        "exit": lambda _: print("Good bye!"),
        "phone": lambda args: search_contact(args[0], phonebook),
        "add-birthday": lambda args: add_birthday(args[0], args[1], phonebook),
        "show-birthday": lambda args: show_birthday(args[0], phonebook),
        "birthdays": lambda _: birthdays(phonebook)
        }

    while True:
        command = input("command: ").strip().split()
        cmd = command[0].lower()
        args = command[1:]

        if cmd in ["close", "exit"]:
            commands[cmd](args)
            break
        elif cmd in commands:
            try:
                commands[cmd](args)
            except Exception as e:
                print("[ERROR]", e)
        else:
            print("Invalid command.")
            print("Available commands: hello, add, change, delete, search, show, phone, add-birthday, show-birthday, "
                  "birthdays, close, exit")
        # finally:
        #     save_phonebook(phonebook)


if __name__ == '__main__':
    # phonebook = load_phonebook()
    main()
    # save_phonebook(phonebook)
