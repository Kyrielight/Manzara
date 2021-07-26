import re

from definitions.arguments_command import Usagi12WithArgumentsCommand
from typing import Optional, Tuple
from urllib.parse import quote

class Google(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str]) -> str:
        """
        The Google redirect is a bit special because everything gets
        defaulted here too, so we need to check if the bindings match.
        """
        if len(args) > 0:
            args = ' '.join(args)
            if self.bindings[0].match(args):
                return 'https://www.google.com/search?q={}'.format(quote(args[1:]))
            else:
                return 'https://www.google.com/search?q={}'.format(quote(args))
        else:
            return 'https://www.google.com'

    @property
    def description(self) -> str:
        return """For making searches on Google"""

    @property
    def bindings(self) -> Optional[Tuple[re.Pattern]]:
        return (
            re.compile(r'^(?:g|google)(?:\ .+)?$', re.IGNORECASE),
        )

    @property
    def triggers(self) -> Optional[Tuple[str]]:
        return None