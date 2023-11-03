from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.padding import Padding


class RichFormatter:
    __instance = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(RichFormatter, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.console = Console()

    def print(self, text, style=None):
        self.console.print(text, style=style)

    def input(self, text):
        return self.console.input(text)

    def format_command_list(self, commands):
        table = Table(title="Available Commands")
        table.add_column("Command", style="bold")
        table.add_column("Description")

        for command in commands:
            table.add_row(command.name, Text(command.description))
            table.add_row(Padding("", (0, 1)))

        self.print(table)

    def format_field_value_pair(self, field: str, value: str):
        return f"[bold medium_spring_green]{field}[/bold medium_spring_green]: [royal_blue1]{value}[/royal_blue1]"
