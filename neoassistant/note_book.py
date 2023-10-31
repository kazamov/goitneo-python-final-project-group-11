from collections import UserDict


class Note:
    def __init__(self, title: str, content: str, tags: list[str] = None):
        self.title = title
        self.content = content
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    def __str__(self):
        return f"Title: {self.title}\nContent: {self.content}\nTags: {', '.join(self.tags)}"


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

    def edit(self, title: str, new_title: str, new_content: str, new_tags: list[str]):
        note = self.find(title)
        if note:
            note.title = new_title
            note.content = new_content
            note.tags = new_tags
            self.data[new_title] = note
            self.data.pop(title)

    def search(self, tag: str) -> list[Note]:
        notes = []
        for note in self.data.values():
            if tag in note.tags:
                notes.append(note)
        return notes
