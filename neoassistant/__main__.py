from .assistant import Neoassistant
from .commands import get_command, get_suggested_commands, parse_input
from .rich_formatter import RichFormatter

NEOASSISTANT_DATA_FILENAME = "neoassistant-data.bin"
formatter = RichFormatter()


def main():
    neoassistant = Neoassistant()
    neoassistant.load(NEOASSISTANT_DATA_FILENAME)


    formatter.format_and_print(
        "Welcome to the neoassistant bot!",
        style="orange1")
    while True:
        user_input = input("Enter a command: ")
        command_name, *args = parse_input(user_input)

        command_object = get_command(command_name)

        if command_object:
            result = command_object.execute(neoassistant, args)
            formatter.format_and_print(f"\n{result}", style="green")

            if command_object.is_final:
                neoassistant.save(NEOASSISTANT_DATA_FILENAME)
                break
        else:
            suggested_commands = get_suggested_commands(command_name)

            if len(suggested_commands) == 0:
                formatter.format_and_print("Unknown command.", style="red")
            else:
                print(f"Did you mean: {', '.join(suggested_commands)}?")


if __name__ == "__main__":
    main()
