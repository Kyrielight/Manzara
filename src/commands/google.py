import re

from definitions.arguments_command import ManzaraWithArgumentsCommand
from typing import List
from urllib.parse import quote

class Google(ManzaraWithArgumentsCommand):

    def redirect(self, args: List[str]) -> str:
        if len(args) > 1:
            return 'https://google.com/search?q={}'.format(quote(' '.join(args)))
        else:
            return 'https://www.google.com'

    @property
    def description(self) -> str:
        return """For making searches on Google"""

    @property
    def bindings(self) -> List[re.Pattern]:
        return [
            re.compile(r'^(?:g|google)(?:\ .+)?$', re.IGNORECASE),
        ]