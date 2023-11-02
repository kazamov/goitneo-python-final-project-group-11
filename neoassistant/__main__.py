from .assistant import Neoassistant
from .commands import get_command, get_suggested_commands, parse_input


NEOASSISTANT_DATA_FILENAME = "neoassistant-data.bin"


def main():
    neoassistant = Neoassistant()
    neoassistant.load(NEOASSISTANT_DATA_FILENAME)

    print("Welcome to the neoassistant bot!")
    while True:
        try:
            user_input = input("Enter a command: ")
            command_name, *args = parse_input(user_input)

            command_object = get_command(command_name)

            if command_object:
                print(f"\n{command_object.execute(neoassistant, args)}\n")

                if command_object.is_final:
                    neoassistant.save(NEOASSISTANT_DATA_FILENAME)
                    break
            else:
                suggested_commands = get_suggested_commands(command_name)

                if len(suggested_commands) == 0:
                    print("Unknown command.")
                else:
                    print(f"Did you mean: {', '.join(suggested_commands)}?")
        except KeyboardInterrupt:
            print("\nGood bye!")
            neoassistant.save(NEOASSISTANT_DATA_FILENAME)
            break


if __name__ == "__main__":
    main()
