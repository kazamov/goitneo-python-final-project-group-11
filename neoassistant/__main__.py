from .assistant import Neoassistant
from .commands import get_command, get_suggested_commands, parse_input
from .rich_formatter import RichFormatter


NEOASSISTANT_DATA_FILENAME = "neoassistant-data.bin"


def main():
    formatter = RichFormatter()

    neoassistant = Neoassistant()
    neoassistant.load(NEOASSISTANT_DATA_FILENAME)

    formatter.print("Welcome to the neoassistant bot!", style="orange1")
    while True:
        try:
            user_input = formatter.input("[grey70]\nEnter the command\n>>> [/grey70] ")
            command_name, *args = parse_input(user_input)

            command_object = get_command(command_name)

            if command_object:
                result = command_object.execute(neoassistant, args)
                formatter.print(f"\n{result}")

                if command_object.is_final:
                    neoassistant.save(NEOASSISTANT_DATA_FILENAME)
                    break
            else:
                suggested_commands = get_suggested_commands(command_name)

                if len(suggested_commands) == 0:
                    formatter.print("Unknown command.", style="red")
                else:
                    formatter.print(f"\nDid you mean: {', '.join(suggested_commands)}?")

        except KeyboardInterrupt:
            formatter.print("\nGood bye!")
            neoassistant.save(NEOASSISTANT_DATA_FILENAME)
            break


if __name__ == "__main__":
    main()
