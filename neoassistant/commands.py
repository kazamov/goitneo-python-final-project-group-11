from abc import ABC, abstractmethod

from .assiatant import Assistant

from .contact_book import ContactBook, Contact
from .errors import InvalidCommandError, InvalidValueFieldError


def input_error(func):
    """Decorator for input errors"""

    def inner(self, address_book: ContactBook, args):
        try:
            return func(self, address_book, args)

        except InvalidCommandError as e:
            return e.message
        except InvalidValueFieldError as e:
            return e.message

    return inner


class Command(ABC):
    """Abstract class for commands"""

    def __init__(
        self, name: str, description: str, alias: str = None, is_final: bool = False
    ):
        self.name = name
        self.description = description
        self.alias = alias
        self.is_final = is_final

    def __str__(self):
        return f"{self.name} - {self.description}"

    @abstractmethod
    def execute(self, assistant: Assistant, args):
        pass


class HelloCommand(Command):
    def __init__(self):
        super().__init__("hello", "Show greeting message.")

    def execute(self, *_):
        return "How can I help you?"


class AddContactCommand(Command):
    def __init__(self):
        super().__init__(
            "add",
            "Add a new contact. Format: add <name> <phone> [birthday]",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) < 2:
            raise InvalidCommandError(self.name, "Name and phone are required.")

        name = ""
        phone = ""
        birthday = None

        try:
            name, phone, birthday = args
        except ValueError:
            name, phone = args

        record = assistant.contact_book.find(name)
        if record:
            record.add_phone(phone)
            if birthday:
                record.add_birthday(birthday)
            return "Contact updated."

        record = Contact(name)
        record.add_phone(phone)

        if birthday:
            record.add_birthday(birthday)

        assistant.contact_book.add_record(record)

        return "Contact added."


class ChangeContactCommand(Command):
    def __init__(self):
        super().__init__(
            "change",
            "Change a phone number of a contact. Format: change <name> <prev_phone> <new_phone> [birthday]",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) < 3:
            raise InvalidCommandError(
                self.name, "Name, previous phone and new phone are required."
            )

        name = ""
        prev_phone = ""
        new_phone = ""
        birthday = None

        try:
            name, prev_phone, new_phone, birthday = args
        except ValueError:
            name, prev_phone, new_phone = args

        record = assistant.contact_book.find(name)
        if record:
            record.edit_phone(prev_phone, new_phone)

            if birthday:
                record.add_birthday(birthday)

            return "Contact updated."
        else:
            return "Contact is not found."


class DeleteContactCommand(Command):
    def __init__(self):
        super().__init__(
            "delete",
            "Delete a phone number of a contact. Format: delete <name> <phone>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) != 2:
            raise InvalidCommandError(self.name, "Name and phone are required.")

        name, phone = args

        record = assistant.contact_book.find(name)
        if record:
            record.delete_phone(phone)
            return "Contact updated."
        else:
            return "Contact is not found."


class ShowContactCommand(Command):
    def __init__(self):
        super().__init__(
            "show",
            "Show contact information. Format: show <name>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) != 1:
            raise InvalidCommandError(self.name, "Name is required.")

        name = args[0]

        record = assistant.contact_book.find(name)
        if record:
            return str(record)
        else:
            return "Contact is not found."


class ShowAllContactsCommand(Command):
    def __init__(self):
        super().__init__("all", "Show all contacts.")

    def execute(self, assistant: Assistant, _):
        return str(assistant.contact_book)


class AddBirthdayCommand(Command):
    def __init__(self):
        super().__init__(
            "add-birthday",
            "Add a birthday to a contact. Format: add-birthday <name> <birthday>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) != 2:
            raise InvalidCommandError(self.name, "Name and birthday are required.")

        name, birthday = args

        record = assistant.contact_book.find(name)
        if record:
            record.add_birthday(birthday)
            return "Birthday added."
        else:
            return "Contact is not found."


class ChangeBirthdayCommand(Command):
    def __init__(self):
        super().__init__(
            "change-birthday",
            "Change a birthday of a contact. Format: change-birthday <name> <birthday>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) != 2:
            raise InvalidCommandError(self.name, "Name and birthday are required.")

        name, birthday = args

        record = assistant.contact_book.find(name)
        if record:
            record.add_birthday(birthday)
            return "Birthday updated."
        else:
            return "Contact is not found."


class ShowBirthdayCommand(Command):
    def __init__(self):
        super().__init__(
            "show-birthday",
            "Show a birthday of a contact. Format: show-birthday <name>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) != 1:
            raise InvalidCommandError(self.name, "Name is required.")

        name = args[0]

        record = assistant.contact_book.find(name)
        if record:
            return str(record.birthday)
        else:
            return "Contact is not found."


class ShowBirthdaysCommand(Command):
    def __init__(self):
        super().__init__("show-birthdays", "Show all birthdays per next 7 days.")

    def execute(self, assistant: Assistant, _):
        return assistant.contact_book.get_birthdays_per_week()


class ExitCommand(Command):
    def __init__(self):
        super().__init__("exit", "Exit the program.", alias="close", is_final=True)

    def execute(self, *_):
        return "Good bye!"


class HelpCommand(Command):
    def __init__(self):
        super().__init__(
            "help",
            "Show all available commands or a single command info. Format: help [command]",
        )

    def execute(self, _, args):
        if len(args) > 0:
            command_name = args[0]
            command = get_command(command_name)
            if command:
                return str(command)

            return f"Command '{command_name}' is not found."

        return "\n".join(str(c) for c in COMMANDS)


COMMANDS = [
    HelloCommand(),
    AddContactCommand(),
    ChangeContactCommand(),
    DeleteContactCommand(),
    ShowContactCommand(),
    ShowAllContactsCommand(),
    AddBirthdayCommand(),
    ChangeBirthdayCommand(),
    ShowBirthdayCommand(),
    ShowBirthdaysCommand(),
    ExitCommand(),
    HelpCommand(),
]

COMMANDS_MAP = {(c.name, c.alias): c for c in COMMANDS}


def get_command(command_name: str):
    command = None
    for keys, handler in COMMANDS_MAP.items():
        if command_name in keys:
            command = handler
            break
    return command
