from collections import UserDict, defaultdict
from datetime import datetime

from .fields import Name, Phone, Birthday, Email, Address


class Contact:
    """Class for contact"""

    def __init__(self, name: str):
        self.name = Name(name)
        self.birthday: Birthday = None
        self.phones: list[Phone] = []
        self.address: Address = None
        self.email: Email = None

    def __str__(self):
        result = f"Name: {self.name.value}\n"

        if len(self.phones) > 0:
            result += f"Phones: {', '.join(p.value for p in self.phones)}\n"

        if self.birthday:
            result += f"Birthday: {str(self.birthday)}\n"

        if self.address:
            result += f"Address: {str(self.address)}\n"

        if self.email:
            result += f"Email: {self.email.value}\n"

        return result

    def set_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def set_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def set_email(self, email: str):
        self.email = Email(email)

    def set_address(self, address: str):
        self.address = Address(address)


class ContactBook(UserDict):
    """Class for contact book"""

    def __str__(self) -> str:
        if len(self.data) == 0:
            return "Contact book is empty."

        return "\n".join(
            str(record) for record in self.sort_by_name(self.data.values())
        )

    def add(self, contact: Contact):
        self.data[contact.name.value] = contact

    def find(self, name: str) -> Contact:
        return self.data[name] if name in self.data else None

    def delete(self, name: str):
        if name in self.data:
            self.data.pop(name)

    def get_birthdays_per_week(self, days_delta=7):
        user_records = self.data.values()

        if len(user_records) == 0:
            return "No users found."

        birthdays_list = defaultdict(list)
        current_date = datetime.now().date()

        for record in user_records:
            name = record.name.value
            birthday = record.birthday.value

            if not birthday:
                continue

            birthday_this_year = birthday.replace(year=current_date.year)

            if birthday_this_year < current_date:
                birthday_this_year = birthday_this_year.replace(
                    year=current_date.year + 1
                )

            delta_days = (birthday_this_year - current_date).days
            if delta_days > 0 and delta_days <= days_delta:
                birthdays_list[birthday_this_year].append(name)

        if len(birthdays_list) == 0:
            return f"No birthdays near {days_delta} days."

        sorted_birthdays_list = sorted(birthdays_list.keys())

        result = f"Birthdays for the next {days_delta} days:\n"
        for day in sorted_birthdays_list:
            result += f"{day.strftime('%d.%m.%Y')} - {', '.join(birthdays_list[day])}\n"

        return result

    def filter(self, search_criteria: str) -> list[Contact]:
        return self.sort_by_name(
            list(
                filter(
                    lambda contact: str(contact).find(search_criteria) > 0,
                    self.data.values(),
                )
            )
        )

    def sort_by_name(self, contacts: list[Contact]) -> list[Contact]:
        return sorted(contacts, key=lambda contact: contact.name.value)
