import re

from collections import defaultdict
from langcodes import Language
from src.definitions.arguments_command import Usagi12WithArgumentsCommand
from typing import Optional, Tuple
from urllib.parse import quote

BASE_URLS = defaultdict(lambda: "https://www.google.com/", {
    'ja': "https://www.google.co.jp/",
    'jp': "https://www.google.co.jp/",
})

SEARCH = "search?q={}"

class Google(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str], language: Optional[Language]) -> str:
        """
        The Google redirect is a bit special because everything gets
        defaulted here too, so we need to check if the bindings match.
        """
        if len(args) > 0:
            args = ' '.join(args)
            if self.bindings[0].match(args):
                return BASE_URLS[str(language)] + SEARCH.format(quote(args[1:]))
            else:
                return BASE_URLS[str(language)] + SEARCH.format(quote(args))
        else:
            return BASE_URLS[str(language)]

    @property
    def description(self) -> str:
        return """For making searches on Google"""

    @property
    def bindings(self) -> Optional[Tuple[re.Pattern]]:
        return (
            re.compile(r'^(?:g|google)(?:\ .+)?$', re.IGNORECASE),
        )

    @property
    def slashes(self) -> Optional[Tuple[str]]:
        return None

    @property
    def triggers(self) -> Optional[Tuple[str]]:
        return None

    @property
    def languages(self) -> Optional[Tuple[str]]:
        return (
            'en',
            'ja',
            'jp'
        )