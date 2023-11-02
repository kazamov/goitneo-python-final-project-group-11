from abc import ABC, abstractmethod
from argparse import ArgumentParser
from shlex import split

from .note_book import Note
from .assistant import Assistant
from .contact_book import ContactBook, Contact
from .errors import InvalidCommandError, InvalidValueFieldError


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


class AddContactCommand(Command):
    def __init__(self):
        super().__init__(
            "add",
            "Add a new contact. Format: add --name <name> --phones [phone] --birthday [birthday] --address [address] --email [email]",
        )
        self.parser = ArgumentParser()
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
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

        name = parsed_args.get("name")
        phones = parsed_args.get("phones")
        birthday = parsed_args.get("birthday")
        address = parsed_args.get("address")
        email = parsed_args.get("email")

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
            "Change a contact. Format: change --current-name <current-name> --name [name] --phones [phone] --birthday [birthday] --address [address] --email [email]",
        )
        self.parser = ArgumentParser()
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
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

        current_name = parsed_args.get("current_name")
        name = parsed_args.get("name")
        phones = parsed_args.get("phones")
        birthday = parsed_args.get("birthday")
        address = parsed_args.get("address")
        email = parsed_args.get("email")

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
            "Delete a contact. Format: delete --name <name>",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-n", "--name", type=str, required=True)

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

        name = parsed_args.get("name")

        contact = assistant.contact_book.find(name)

        if not contact:
            return f"Contact with name '{name}' is not found."

        assistant.contact_book.delete(name)
        return "Contact deleted."


class ShowContactCommand(Command):
    def __init__(self):
        super().__init__(
            "show",
            "Show contact information. Format: show --name <name>",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-n", "--name", type=str, required=True)

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

        name = parsed_args.get("name")

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
            "Show all birthdays per the next specified number of days."
            + "Format: show-birthdays --days <days> (default 7)",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-d", "--days", type=int, required=False, default=7)

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

        days_delta = parsed_args.get("days")

        if days_delta < 2:
            raise InvalidCommandError(self.name, "The minimum value for 'days' is 2.")

        if days_delta > 365:
            raise InvalidCommandError(self.name, "The maximum value for 'days' is 365.")

        return assistant.contact_book.get_birthdays_per_week(days_delta)


class FilterContactsCommand(Command):
    def __init__(self):
        super().__init__(
            "filter",
            "Filter contacts by search criteria. Format: filter --criteria <search_criteria>",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-cr", "--criteria", type=str, required=True)

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

        criteria = parsed_args.get("criteria")

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
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

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
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

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
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

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
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

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


class FilterNotesCommand(Command):
    def __init__(self):
        super().__init__(
            "filter-notes",
            "Filter notes by criteria. Format: filter-notes --criteria <criteria>",
        )
        self.parser = ArgumentParser()
        self.parser.add_argument("-cr", "--criteria", type=str, required=True)

    @input_error
    def execute(self, assistant: Assistant, args):
        try:
            parsed_args = vars(self.parser.parse_args(args))
        except SystemExit as exc:
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

        criteria = parsed_args.get("criteria")

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
            "Filter notes by tags. Format: filter-notes-by-tags --tags [tags]",
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
            raise InvalidCommandError(self.name, "Invalid arguments") from exc

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
        if levenshtein_distance(command_name, valid_command) <= 2:
            suggested_commands.append(valid_command)
    return suggested_commands
