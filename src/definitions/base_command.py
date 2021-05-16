from abc import ABC, abstractmethod
from typing import List
from re import Pattern

class ManzaraBaseCommand(ABC):

    @property
    @abstractmethod
    def bindings(self) -> List[Pattern]:
        """
        Return a list of bindings represented as re.Pattern objects.
        Note: Manzara will call .strip() on the passed in command before checking x.bindings().
        Used by Manzara to determine where to send commands.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Provide a description of this command.
        """
        pass