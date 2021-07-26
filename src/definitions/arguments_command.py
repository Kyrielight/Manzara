from abc import abstractmethod
from .base_command import Usagi12BaseCommand

from typing import Tuple

class Usagi12WithArgumentsCommand(Usagi12BaseCommand):

    @abstractmethod
    def redirect(self, args: Tuple[str]) -> str:
        """
        A Usagi12 command that gets arguments passed in with it.

        Params:
        - args: A list of strings representing the input that gets called with .strip(), then .split()
                Argument 0 includes the actual argument passed in.

        Return: A url string that Usagi12 will redirect the user to.
        """
        pass

class Usagi12WithoutArgumentsCommand(Usagi12BaseCommand):

    @abstractmethod
    def redirect(self) -> str:
        """
        A Usagi12 command that does not have arguments passed.

        Return: A url string that Usagi12 will redirect the user to.
        """
        pass