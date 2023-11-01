from collections import UserDict, defaultdict
from datetime import datetime, timedelta

from .fields import Name, Phone, Birthday, Email, Address


class Contact:
    """Class for contact"""

    def __init__(self, name, email=None):
        self.name = Name(name)
        self.birthday: Birthday = None
        self.phones: list[Phone] = []
        self.address: Address = None
        self.email = None  # Initialize the email field if provided
        if email:
            self.add_email(email)

    def __str__(self):
        result = f"Contact name: {self.name.value}, phones: {', '.join(p.value for p in self.phones)}"

        if self.birthday:
            result += f", birthday: {str(self.birthday)}"

        if self.address:
            result += f", address: {str(self.address)}"

        if self.email:  # Add email to the string representation
            result += f", email: {self.email.value}"

        return result

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone_str: str):
        phone = self.find_phone(phone_str)
        if phone:
            self.phones.remove(phone)

    def edit_phone(self, prev_phone: str, next_phone: str):
        phone = self.find_phone(prev_phone)
        if phone:
            phone.value = next_phone

    def find_phone(self, phone_str: str) -> Phone:
        phone = None
        for p in self.phones:
            if p.value == phone_str:
                phone = p
                break
        return phone

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def add_email(self, email: str):
        self.email = Email(email)

    def change_email(self, new_email: str):
        if self.email:
            self.email.value = new_email
        else:
            self.add_email(new_email)

    def delete_email(self):
        self.email = None

    def show_email(self):
        return self.email.value if self.email else None

    def add_address(self, address: str):
        self.address = Address(address)

    def delete_address(self):
        self.address = None

    def show_address(self) -> Address:
        return self.address


class ContactBook(UserDict):
    """Class for contact book"""

    def __str__(self) -> str:
        if len(self.data) == 0:
            return "Contact book is empty."

        return "\n".join(str(record) for record in self.data.values())

    def add_record(self, record: Contact):
        self.data[record.name.value] = record

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
        return list(
            filter(
                lambda contact: str(contact).find(search_criteria) > 0,
                self.data.values(),
            )
        )
