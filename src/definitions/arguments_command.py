from abc import abstractmethod
from .base_command import ManzaraBaseCommand

from typing import Tuple

class ManzaraWithArgumentsCommand(ManzaraBaseCommand):

    @abstractmethod
    def redirect(self, args: Tuple[str]) -> str:
        """
        A Manzara command that gets arguments passed in with it.

        Params:
        - args: A list of strings representing the input that gets called with .strip(), then .split()
                Argument 0 includes the actual argument passed in.
        
        Return: A url string that Manzara will redirect the user to.
        """
        pass