from abc import ABC, abstractmethod
from langcodes import Language
from typing import Optional, Tuple
from re import Pattern

class Usagi12BaseCommand(ABC):

    @property
    @abstractmethod
    def bindings(self) -> Optional[Tuple[Pattern]]:
        """
        Return a list of bindings represented as re.Pattern objects.
        Note: Usagi12 will call .strip() on the passed in command before checking x.bindings().
        Used by Usagi12 to determine where to send commands.
        """
        pass

    @property
    @abstractmethod
    def triggers(self) -> Optional[Tuple[str]]:
        """
        Return a list of strings that act as "triggers". Instead of matching regex, this will
        match the words provided and pass to the redirect. Is not case-sensitive.
        Note: Usagi12 will call .strip() on the passed in command before checking x.triggers()
        Used by Usagi12 to determine where to send commands.
        """
        pass

    @property
    @abstractmethod
    def slashes(self) -> Optional[Tuple[str]]:
        """
        Return a list of strings that can act as "slash" commands. Instead of matching regex,
        this will follow a pattern of "command/<optional: query>". Is not case-sensitive.
        Note: Usagi12 will call .strip() on the passed in command before checking x.slashes().
        Used by Usagi12 to determine where to send commands.
        """
        pass

    @property
    @abstractmethod
    def languages(self) -> Optional[Tuple[str]]:
        """
        Indicate which locales are supported by this module.
        Leave empty if the language does not matter (i.e. same link is always returned).
        Should be something like, "en-US" or "en-JA"
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Provide a description of this command.
        """
        pass

