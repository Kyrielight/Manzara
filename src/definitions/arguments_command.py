from abc import abstractmethod
from .base_command import Usagi12BaseCommand

from langcodes import Language

from typing import Tuple

class Usagi12WithArgumentsCommand(Usagi12BaseCommand):

    @abstractmethod
    def redirect(self, args: Tuple[str], language: Language) -> str:
        """
        A Usagi12 command that gets arguments passed in with it.

        Params:
        - args: A list of strings representing the input that gets called with .strip(), then .split()
                Argument 0 includes the actual argument passed in.
        - language: Locale to use, as defined by the best available language from the user and the
                languages specified in Usagi12BaseCommand. Defaults to None.

        Return: A url string that Usagi12 will redirect the user to.
        """
        pass

class Usagi12WithoutArgumentsCommand(Usagi12BaseCommand):

    @abstractmethod
    def redirect(self, language: Language) -> str:
        """
        A Usagi12 command that does not have arguments passed.

        Params:
        - language: Locale to use, as defined by the best available language from the user and the
                languages specified in Usagi12BaseCommand. Defaults to None.

        Return: A url string that Usagi12 will redirect the user to.
        """
        pass