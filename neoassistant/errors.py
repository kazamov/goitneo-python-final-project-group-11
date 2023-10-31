class ApplicationError(Exception):
    """Base class for all application errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidCommandError(ApplicationError):
    """Raised when an invalid command is provided."""

    def __init__(self, command: str, message: str = None):
        self.command = command
        self.message = f"The command '{self.command}' is invalid."

        if message:
            self.message += f"\n{message}"

        super().__init__(self.message)


class InvalidValueFieldError(ApplicationError):
    """Raised when a field value is invalid."""

    def __init__(self, field_name: str, field_value: str, message: str = None):
        self.field_name = field_name
        self.field_value = field_value
        self.message = (
            f"The value '{self.field_value}' is invalid for field '{self.field_name}'."
        )
        if message:
            self.message += f"\n{message}"

        super().__init__(self.message)
