from abc import ABC, abstractmethod
from typing import Tuple 
from re import Pattern

class Usagi12BaseCommand(ABC):

    @property
    @abstractmethod
    def bindings(self) -> Tuple[Pattern]:
        """
        Return a list of bindings represented as re.Pattern objects.
        Note: Usagi12 will call .strip() on the passed in command before checking x.bindings().
        Used by Usagi12 to determine where to send commands.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Provide a description of this command.
        """
        pass