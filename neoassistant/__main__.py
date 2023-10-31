from .contact_book import ContactBook
from .commands import get_command


CONTACT_BOOK_FILENAME = "address_book.pickle"


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def main():
    contact_book = ContactBook()
    contact_book.load(CONTACT_BOOK_FILENAME)

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command_name, *args = parse_input(user_input)

        command_object = get_command(command_name)

        if command_object:
            print(f"\n{command_object.execute(contact_book, args)}\n")

            if command_object.is_final:
                contact_book.save(CONTACT_BOOK_FILENAME)
                break
        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()
