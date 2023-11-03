from argparse import ArgumentError, ArgumentParser


class AssistantArgumentParser(ArgumentParser):
    def __init__(self, command_name: str = "", description: str = ""):
        super().__init__(
            exit_on_error=False,
            prog=command_name,
            description=description,
            add_help=False,
        )

    def _get_usage_message(self) -> str:
        return self.format_usage().capitalize()

    def error(self, message: str):
        raise ArgumentError(
            None, f"{message.capitalize()}\n{self._get_usage_message()}"
        )

    def get_short_description(self) -> str:
        formatter = self._get_formatter()

        # description
        formatter.add_text(self.description)

        # usage
        formatter.add_usage(
            self.usage, self._actions, self._mutually_exclusive_groups, prefix="Usage: "
        )

        # determine help from format above
        return formatter.format_help()

    def get_help_message(self) -> str:
        formatter = self._get_formatter()

        # description
        formatter.add_text(self.description)

        # usage
        formatter.add_usage(
            self.usage, self._actions, self._mutually_exclusive_groups, prefix="Usage: "
        )

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()
