from abc import ABC, abstractmethod
from pathlib import Path
from pickle import dump, load

from .contact_book import ContactBook


class Assistant(ABC):
    """Abstract class for neoassistant"""

    @property
    @abstractmethod
    def contact_book(self) -> ContactBook:
        pass

    @abstractmethod
    def save(self, filename):
        pass

    @abstractmethod
    def load(self, filename):
        pass


class Neoassistant(Assistant):
    def __init__(self):
        self.__contact_book = ContactBook()

    @property
    def contact_book(self) -> ContactBook:
        return self.__contact_book

    def save(self, filename):
        cache_folder_path = Path.joinpath(Path.cwd(), "cache")
        cache_folder_path.mkdir(exist_ok=True)
        file_path = Path.joinpath(cache_folder_path, filename)
        with open(file_path, "wb") as file:
            dump(self, file)

    def load(self, filename):
        path = Path.joinpath(Path.cwd(), "cache", filename)
        if path.exists():
            with open(path, "rb") as file:
                content = load(file)
                self.__contact_book = content.contact_book
