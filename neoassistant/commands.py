from abc import ABC, abstractmethod
from argparse import ArgumentParser, ArgumentError
from shlex import split

from .argument_parser import AssistantArgumentParser

from .note_book import Note
from .assistant import Assistant
from .contact_book import ContactBook, Contact
from .errors import InvalidCommandError, InvalidValueFieldError
from .rich_formatter import RichFormatter


def levenshtein_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    return dp[m][n]


def parse_input(user_input):
    """Parse input string and return command name and arguments"""
    cmd, *args = split(user_input)
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    """Decorator for input errors"""

    def inner(self, address_book: ContactBook, args):
        try:
            return func(self, address_book, args)

        except InvalidCommandError as e:
            return f"[red]{e.message}[/red]"
        except InvalidValueFieldError as e:
            return f"[red]{e.message}[/red]"

    return inner


def parse_arguments(func):
    """Decorator to parse command arguments"""

    def inner(self, address_book: ContactBook, args):
        try:
            args = vars(self.parser.parse_args(args))
            return func(self, address_book, args)
        except ArgumentError as exc:
            raise InvalidCommandError(self.name, exc.message) from exc

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
        self.parser = AssistantArgumentParser(name, description)

    def __str__(self):
        return self.parser.get_help_message()

    def get_short_description(self):
        return self.parser.get_short_description()

    @abstractmethod
    def execute(self, assistant: Assistant, args: dict):
        pass


class AddContactCommand(Command):
    def __init__(self):
        super().__init__(
            "add",
            "Add a new contact.",
        )
        self.parser.add_argument("-n", "--name", type=str, required=True)
        self.parser.add_argument(
            "-p",
            "--phones",
            action="extend",
            nargs="+",
            type=str,
            required=False,
            default=[],
        )
        self.parser.add_argument(
            "-b", "--birthday", type=str, required=False, default=None
        )
        self.parser.add_argument(
            "-a", "--address", type=str, required=False, default=None
        )
        self.parser.add_argument(
            "-e", "--email", type=str, required=False, default=None
        )

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        name = args.get("name")
        phones = args.get("phones")
        birthday = args.get("birthday")
        address = args.get("address")
        email = args.get("email")

        contact = assistant.contact_book.find(name)
        if contact:
            return f"Contact with name '{name}' already exists."

        contact = Contact(name)

        if len(phones) > 0:
            for phone in phones:
                contact.set_phone(phone)

        if birthday:
            contact.set_birthday(birthday)

        if address:
            contact.set_address(address)

        if email:
            contact.set_email(email)

        assistant.contact_book.add(contact)

        return "Contact added."


class ChangeContactCommand(Command):
    def __init__(self):
        super().__init__(
            "change",
            "Change a contact.",
        )
        self.parser = AssistantArgumentParser("add", "Add a new contact.")
        self.parser.add_argument("-cn", "--current-name", type=str, required=True)
        self.parser.add_argument("-n", "--name", type=str, required=False)
        self.parser.add_argument(
            "-p",
            "--phones",
            action="extend",
            nargs="+",
            type=str,
            required=False,
            default=[],
        )
        self.parser.add_argument(
            "-b", "--birthday", type=str, required=False, default=None
        )
        self.parser.add_argument(
            "-a", "--address", type=str, required=False, default=None
        )
        self.parser.add_argument(
            "-e", "--email", type=str, required=False, default=None
        )

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        current_name = args.get("current_name")
        name = args.get("name")
        phones = args.get("phones")
        birthday = args.get("birthday")
        address = args.get("address")
        email = args.get("email")

        contact = assistant.contact_book.find(current_name)

        if not contact:
            return f"Contact with name '{current_name}' is not found."

        if len(phones) > 0:
            contact.phones.clear()
            for phone in phones:
                contact.set_phone(phone)

        if birthday:
            contact.set_birthday(birthday)

        if address:
            contact.set_address(address)

        if email:
            contact.set_email(email)

        if name and name != current_name:
            assistant.contact_book.delete(current_name)
            contact.name.value = name
            assistant.contact_book.add(contact)

        return "Contact updated."


class DeleteContactCommand(Command):
    def __init__(self):
        super().__init__(
            "delete",
            "Delete a contact.",
        )

        self.parser.add_argument("-n", "--name", type=str, required=True)

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        name = args.get("name")

        contact = assistant.contact_book.find(name)

        if not contact:
            return f"Contact with name '{name}' is not found."

        assistant.contact_book.delete(name)
        return "Contact deleted."


class ShowContactCommand(Command):
    def __init__(self):
        super().__init__(
            "show",
            "Show contact information.",
        )

        self.parser.add_argument("-n", "--name", type=str, required=True)

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        name = args.get("name")

        contact = assistant.contact_book.find(name)

        if not contact:
            return f"Contact with name '{name}' is not found."

        return str(contact)


class ShowAllContactsCommand(Command):
    def __init__(self):
        super().__init__("all", "Show all contacts.")

    def execute(self, assistant: Assistant, _):
        return str(assistant.contact_book)


class ShowBirthdaysCommand(Command):
    def __init__(self):
        super().__init__(
            "show-birthdays",
            "Show all birthdays per the next specified number of days.",
        )

        self.parser.add_argument("-d", "--days", type=int, required=False, default=7)

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        days_delta = args.get("days")

        if days_delta < 2:
            raise InvalidCommandError(self.name, "The minimum value for 'days' is 2.")

        if days_delta > 365:
            raise InvalidCommandError(self.name, "The maximum value for 'days' is 365.")

        return assistant.contact_book.get_birthdays_per_week(days_delta)


class FilterContactsCommand(Command):
    def __init__(self):
        super().__init__(
            "filter",
            "Filter contacts by search criteria.",
        )

        self.parser.add_argument("-cr", "--criteria", type=str, required=True)

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        criteria = args.get("criteria")

        if len(criteria) < 2:
            raise InvalidCommandError(
                self.name, "The minimum length of 'criteria' is 2 characters."
            )

        contacts = assistant.contact_book.filter(criteria)
        if len(contacts) == 0:
            return f"Contacts that satisfy search criteria '{criteria}' are not found."

        return "\n".join(str(contact) for contact in contacts)


class AddNoteCommand(Command):
    def __init__(self):
        super().__init__(
            "add-note",
            "Add a new note.",
        )

        self.parser.add_argument("-t", "--title", type=str, required=True)
        self.parser.add_argument(
            "-c", "--content", type=str, required=False, default=""
        )
        self.parser.add_argument(
            "--tags", action="extend", nargs="+", type=str, required=False, default=[]
        )

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        title = args.get("title")
        content = args.get("content")
        tags = args.get("tags")

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
            "Change a note.",
        )

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
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        current_title = args.get("current_title")
        title = args.get("title")
        content = args.get("content")
        tags = args.get("tags")

        note = assistant.note_book.find_by_title(current_title)
        if not note:
            return f"Note with title '{current_title}' is not found."

        assistant.note_book.change(current_title, title, content, tags)

        return "Note updated."


class DeleteNoteCommand(Command):
    def __init__(self):
        super().__init__(
            "delete-note",
            "Delete a note.",
        )

        self.parser.add_argument("-t", "--title", type=str, required=True)

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        title = args.get("title")

        note = assistant.note_book.find_by_title(title)

        if not note:
            return f"Note with title '{title}' is not found."

        assistant.note_book.delete(title)

        return "Note deleted."


class ShowNoteCommand(Command):
    def __init__(self):
        super().__init__(
            "show-note",
            "Show a note.",
        )

        self.parser.add_argument(
            "-t", "--title", type=str, required=True, help="Note title"
        )

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        title = args.get("title")

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


class FilterNotesCommand(Command):
    def __init__(self):
        super().__init__(
            "filter-notes",
            "Filter notes by criteria.",
        )

        self.parser.add_argument("-cr", "--criteria", type=str, required=True)

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        criteria = args.get("criteria")

        if len(criteria) < 2:
            raise InvalidCommandError(
                self.name, "The minimum length of 'criteria' is 2 characters."
            )

        notes = assistant.note_book.search(criteria)
        if len(notes) == 0:
            return f"Notes with criteria '{criteria}' are not found."

        return "\n".join(str(note) for note in notes)


class FilterNotesByTagsCommand(Command):
    def __init__(self):
        super().__init__(
            "filter-notes-by-tags",
            "Filter notes by tags.",
        )

        self.parser.add_argument(
            "--tags", action="extend", nargs="+", type=str, required=True
        )

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        tags = args.get("tags")

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
            "Show all available commands or a single command info.",
        )

        self.parser.add_argument("-c", "--command", type=str, required=False)

    @input_error
    @parse_arguments
    def execute(self, assistant: Assistant, args: dict):
        if args.get("command") is not None:
            command_name = args.get("command")
            command = get_command(command_name)
            if command:
                return str(command)
            else:
                suggested_commands = get_suggested_commands(command_name)
                if suggested_commands:
                    return f"Command '{command_name}' not found. Did you mean: {', '.join(suggested_commands)}?"
                else:
                    return f"Command '{command_name}' not found."
        else:
            formatter = RichFormatter()
            formatter.format_command_list(COMMANDS)

        return ""


COMMANDS: list[Command] = [
    AddContactCommand(),
    ChangeContactCommand(),
    DeleteContactCommand(),
    ShowContactCommand(),
    ShowAllContactsCommand(),
    ShowBirthdaysCommand(),
    FilterContactsCommand(),
    AddNoteCommand(),
    ChangeNoteCommand(),
    DeleteNoteCommand(),
    ShowNoteCommand(),
    ShowAllNotesCommand(),
    FilterNotesCommand(),
    FilterNotesByTagsCommand(),
    ExitCommand(),
    HelpCommand(),
]

COMMANDS_MAP = {(c.name, c.alias): c for c in COMMANDS}

VALID_COMMANDS = [c.name for c in COMMANDS]


def get_command(command_name: str):
    command = None
    for keys, handler in COMMANDS_MAP.items():
        if command_name in keys:
            command = handler
            break
    return command


def get_suggested_commands(command_name: str):
    suggested_commands = []
    for valid_command in VALID_COMMANDS:
        if levenshtein_distance(command_name, valid_command) <= 3:
            suggested_commands.append(valid_command)
    return suggested_commands
