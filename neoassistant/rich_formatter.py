from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import style



class RichFormatter:
    def __init__(self):
        self.console = Console()
        self.field_style = style.Style(color="cyan", bold=True)
        self.value_style = style.Style(color="yellow", italic=True)

    def format_and_print(self, text, style=None):
        self.console.print(text, style=style)

    def format_command_list(self, commands):
        table = Table(title="Available Commands")
        table.add_column("Command", style="bold")
        table.add_column("Description")
        
        for command in commands:
            table.add_row(command.name, Text(command.description))
        
        self.console.print(table)
