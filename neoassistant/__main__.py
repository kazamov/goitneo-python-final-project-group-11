from .assistant import Neoassistant
from .commands import get_command


NEOASSISTANT_DATA_FILENAME = "neoassistant-data.bin"


def parse_input(user_input):
    """Parse input string and return command name and arguments"""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def main():
    neoassistant = Neoassistant()
    neoassistant.load(NEOASSISTANT_DATA_FILENAME)

    print("Welcome to the neoassistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command_name, *args = parse_input(user_input)

        command_object = get_command(command_name)

        if command_object:
            print(f"\n{command_object.execute(neoassistant, args)}\n")

            if command_object.is_final:
                neoassistant.save(NEOASSISTANT_DATA_FILENAME)
                break
        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()
