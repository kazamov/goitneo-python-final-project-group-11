from collections import UserDict


class Note:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content

    def __str__(self):
        return f"Title: {self.title}\nContent: {self.content}\n"


class NoteBook(UserDict):
    def __str__(self):
        return "\n".join(str(note) for note in self.data.values())

    def add_record(self, note: Note):
        self.data[note.title] = note

    def find(self, title: str) -> Note:
        return self.data[title] if title in self.data else None

    def delete(self, title: str):
        if title in self.data:
            self.data.pop(title)

    def change(self, title: str, new_title: str, new_content: str):
        note = self.find(title)
        if note:
            note.title = new_title
            note.content = new_content
            self.data[new_title] = note
            self.data.pop(title)

    def search(self, criteria: str) -> list[Note]:
        return list(
            filter(
                lambda note: criteria in note.title or criteria in note.content,
                self.data.values(),
            )
        )
