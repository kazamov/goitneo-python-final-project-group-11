from abc import ABC, abstractmethod
from argparse import ArgumentError, ArgumentParser, ArgumentTypeError

from .note_book import Note
from .assistant import Assistant
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
        super().__init__(
            "show-birthdays",
            "Show all birthdays per the next specified number of days."
            + "Format: show-birthdays <days> (default 7)",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            days_delta = int(args[0])
            if days_delta > 365:
                raise InvalidCommandError(
                    self.name, "The maximum value for days_delta is 365."
                )
        except IndexError:
            days_delta = 7
        except ValueError:
            raise InvalidCommandError(self.name, "Invalid numbers of days.")
        return assistant.contact_book.get_birthdays_per_week(days_delta)

class AddAddressCommand(Command):
    def __init__(self):
        super().__init__(
            "add-address",
            "Add an address to a contact. Format: add-address <name> <address>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) < 2:
            raise InvalidCommandError(self.name, "Name and address are required.")

        name, *address = args

        record = assistant.contact_book.find(name)
        if record:
            record.add_address(' '.join(map(str, address)))
            return "Address added."
        else:
            return "Contact is not found."


class ChangeAddressCommand(Command):
    def __init__(self):
        super().__init__(
            "change-address",
            "Change an address of a contact. Format: change-address <name> <address>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) < 2:
            raise InvalidCommandError(self.name, "Name and address are required.")

        name, *address = args

        record = assistant.contact_book.find(name)
        if record:
            record.add_address(' '.join(map(str, address)))
            return "Address updated."
        else:
            return "Contact is not found."


class ShowAddressCommand(Command):
    def __init__(self):
        super().__init__(
            "show-address",
            "Show an address of a contact. Format: show-address <name>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) != 1:
            raise InvalidCommandError(self.name, "Name is required.")

        name = args[0]

        record = assistant.contact_book.find(name)
        if record:
            return str(record.address)
        else:
            return "Contact is not found."

class DeleteAddressCommand(Command):
    def __init__(self):
        super().__init__(
            "delete-address",
            "Delete an address of a contact. Format: delete-address <name>",
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        if len(args) != 1:
            raise InvalidCommandError(self.name, "Name is required.")

        name = args[0]

        record = assistant.contact_book.find(name)
        if record:
            record.delete_address()
            return "Address is deleted."
        else:
            return "Contact is not found."


class AddNoteCommand(Command):
    def __init__(self):
        super().__init__(
            "add-note",
            "Add a new note. Format: add-note --title <title> --content <content> --tags [tags]",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-t", "--title", type=str, required=True)
        self.parser.add_argument(
            "-c", "--content", type=str, required=False, default=""
        )
        self.parser.add_argument(
            "--tags", action="extend", nargs="+", type=str, required=False, default=[]
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Title is required.") from exc

        title = parsed_args.get("title")
        content = parsed_args.get("content")
        tags = parsed_args.get("tags")

        note = assistant.note_book.find_by_title(title)
        if note:
            return f"Note with title '{title}' already exists."

        note = Note(title, content, tags)
        assistant.note_book.add_record(note)

        return "Note added."


class ChangeNoteCommand(Command):
    def __init__(self):
        super().__init__(
            "change-note",
            "Change a note. Format: change-note --current-title <title> --title [new_title] --content [new_content] --tags [tags]",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-ct", "--current-title", type=str, required=True)
        self.parser.add_argument(
            "-t", "--title", type=str, required=False, default=None
        )
        self.parser.add_argument(
            "-c", "--content", type=str, required=False, default=None
        )
        self.parser.add_argument(
            "--tags", action="extend", nargs="+", type=str, required=False, default=None
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Current title is required.") from exc

        current_title = parsed_args.get("current_title")
        title = parsed_args.get("title")
        content = parsed_args.get("content")
        tags = parsed_args.get("tags")

        note = assistant.note_book.find_by_title(current_title)
        if not note:
            return f"Note with title '{current_title}' is not found."

        assistant.note_book.change(current_title, title, content, tags)

        return "Note updated."


class DeleteNoteCommand(Command):
    def __init__(self):
        super().__init__(
            "delete-note",
            "Delete a note. Format: delete-note --title <title>",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-t", "--title", type=str, required=True)

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Title is required.") from exc

        title = parsed_args.get("title")

        note = assistant.note_book.find_by_title(title)

        if not note:
            return f"Note with title '{title}' is not found."

        assistant.note_book.delete(title)

        return "Note deleted."


class ShowNoteCommand(Command):
    def __init__(self):
        super().__init__(
            "show-note",
            "Show a note. Format: show-note --title <title>",
        )
        self.parser = ArgumentParser(exit_on_error=True)
        self.parser.add_argument(
            "-t", "--title", type=str, required=True, help="Note title"
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Title is required.") from exc

        title = parsed_args.get("title")

        note = assistant.note_book.find_by_title(title)
        if not note:
            return f"Note with title '{title}' is not found."

        return str(note)


class ShowAllNotesCommand(Command):
    def __init__(self):
        super().__init__(
            "all-notes",
            "Show all notes.",
        )

    def execute(self, assistant: Assistant, _):
        return str(assistant.note_book)


class SearchNotesCommand(Command):
    def __init__(self):
        super().__init__(
            "search-notes",
            "Search notes by criteria. Format: search-notes --criteria <criteria>",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-cr", "--criteria", type=str, required=True)

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(
                self.name, "Search criteria is required."
            ) from exc

        criteria = parsed_args.get("criteria")

        notes = assistant.note_book.search(criteria)
        if len(notes) == 0:
            return f"Notes with criteria '{criteria}' are not found."

        return "\n".join(str(note) for note in notes)


class SearchNotesByTagsCommand(Command):
    def __init__(self):
        super().__init__(
            "search-notes-by-tags",
            "Search notes by tags. Format: search-notes-by-tags --tags [tags]",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument(
            "--tags", action="extend", nargs="+", type=str, required=True
        )

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(
                self.name, "At least one tag is required."
            ) from exc

        tags = parsed_args.get("tags")

        notes = assistant.note_book.search_by_tags(tags)
        if len(notes) == 0:
            return f"Notes with tags '{', '.join(tags)}' are not found."

        return "\n".join(str(note) for note in notes)


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
    AddAddressCommand(),
    ChangeAddressCommand(),
    ShowAddressCommand(),
    DeleteAddressCommand(),
    AddNoteCommand(),
    ChangeNoteCommand(),
    DeleteNoteCommand(),
    ShowNoteCommand(),
    ShowAllNotesCommand(),
    SearchNotesCommand(),
    SearchNotesByTagsCommand(),
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
