from datetime import datetime
from abc import ABC

from .errors import InvalidValueFieldError


class Field(ABC):
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
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if len(value) == 0:
            raise InvalidValueFieldError("name", value, "Name cannot be empty.")
        self.__value = value


class Phone(Field):
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
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise InvalidValueFieldError(
                "birthday", value, "Birthday should be in format DD.MM.YYYY."
            )
        else:
            self.__value = parsed_date

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")
