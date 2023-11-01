from datetime import datetime
from abc import ABC
import re

from .errors import InvalidValueFieldError


class Field(ABC):
    """Abstract class for fields"""

    __value = None

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return str(self.value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value


class Name(Field):
    """Class for name field"""

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if len(value) == 0:
            raise InvalidValueFieldError("name", value, "Name cannot be empty.")
        self.__value = value


class Phone(Field):
    """Class for phone field"""

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if len(value) != 10 or not value.isdigit():
            raise InvalidValueFieldError(
                "phone", value, "Phone should contain 10 digits."
            )

        self.__value = value


class Birthday(Field):
    """Class for birthday field"""

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError as exc:
            raise InvalidValueFieldError(
                "birthday", value, "Birthday should be in format DD.MM.YYYY."
            ) from exc
        else:
            self.__value = parsed_date

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Email(Field):
    """Class for email field"""

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if not self.is_valid_email(value):
            raise InvalidValueFieldError(
                "email", value, "Invalid email format."
            )

        self.__value = value

    @staticmethod
    def is_valid_email(email):
        # Use a regular expression to validate email format
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, email) is not None
        
        
class Address(Field):
    """Class for address field"""

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if len(value.strip()) == 0:
            raise InvalidValueFieldError("address", value, "Address cannot be empty.")
        self.__value = value