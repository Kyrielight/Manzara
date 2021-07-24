import re

from definitions.arguments_command import Usagi12WithArgumentsCommand
from typing import Optional, Tuple
from urllib.parse import quote

class Google(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str]) -> str:
        if len(args) > 1:
            return 'https://www.google.com/search?q={}'.format(quote(' '.join(args[1:])))
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