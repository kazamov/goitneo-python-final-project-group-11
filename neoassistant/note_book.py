from collections import UserDict

from .rich_formatter import RichFormatter


formatter = RichFormatter()


class Note:
    def __init__(self, title: str, content: str, tags: list[str]):
        self.title = title
        self.content = content
        self.tags = tags

    def __str__(self):
        result = f"{formatter.format_field_value_pair('Title', self.title)}\n"

        if len(self.content) > 0:
            result += f"{formatter.format_field_value_pair('Content', self.content)}\n"

        if len(self.tags) > 0:
            result += (
                f"{formatter.format_field_value_pair('Tags', ', '.join(self.tags))}\n"
            )
        return result


class NoteBook(UserDict):
    def __str__(self):
        if len(self.data) == 0:
            return "Notebook is empty."

        return "\n".join(str(note) for note in self.sort_by_title(self.data.values()))

    def add_record(self, note: Note):
        self.data[note.title] = note

    def find_by_title(self, title: str) -> Note:
        return self.data[title] if title in self.data else None

    def delete(self, title: str):
        if title in self.data:
            self.data.pop(title)

    def change(
        self,
        current_title: str,
        title: str | None,
        content: str | None,
        tags: list[str] | None,
    ):
        note = self.find_by_title(current_title)
        if note:
            if title:
                note.title = title
            if content:
                note.content = content
            if tags:
                note.tags = tags

            if title and title != current_title:
                self.data[title] = note
                self.data.pop(current_title)

    def search(self, criteria: str) -> list[Note]:
        return self.sort_by_title(
            list(
                filter(
                    lambda note: criteria in note.title or criteria in note.content,
                    self.data.values(),
                )
            )
        )

    def search_by_tags(self, tags: list[str]) -> list[Note]:
        return self.sort_by_title(
            list(
                filter(
                    lambda note: any(tag in note.tags for tag in tags),
                    self.data.values(),
                )
            )
        )

    def sort_by_title(self, notes: list[Note]):
        return sorted(notes, key=lambda note: note.title)
