import re

from langcodes import Language
from src.definitions.arguments_command import Usagi12WithArgumentsCommand
from typing import Optional, Tuple
from urllib.parse import quote

JISHO_URL_BASE  = "https://www.jisho.org/"
JISHO_URL_SEARCH = JISHO_URL_BASE + "search/"
WORDS = quote(" #words")
KANJI = quote(" #kanji")
SENTENCES = quote(" #sentences")
NAMES = quote(" #names")

class Jisho(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str], language: Language) -> str:
        if len(args) > 1:

            root_arg = args[0].lower()
            rest_arg = quote(' '.join(args[1:]))

            # Order by frequency
            if root_arg == "jw":
                return JISHO_URL_SEARCH + rest_arg + WORDS
            elif root_arg == "jk":
                return JISHO_URL_SEARCH + rest_arg + KANJI
            elif root_arg == "jn":
                return JISHO_URL_SEARCH + rest_arg + NAMES
            elif root_arg == "js":
                return JISHO_URL_SEARCH + rest_arg + SENTENCES
            else:
                return JISHO_URL_SEARCH + rest_arg

        else:
            return JISHO_URL_BASE

    @property
    def description(self) -> str:
        return """For making searches on Jisho"""

    @property
    def bindings(self) -> Optional[Tuple[re.Pattern]]:
        return (
            re.compile(r'^j[wksn]?(?:\ .+)?$', re.IGNORECASE),
            re.compile(r'^jisho(?:\ .+)?$', re.IGNORECASE)
        )

    @property
    def triggers(self) -> Optional[Tuple[str]]:
        return None
    
    @property
    def languages(self) -> Optional[Tuple[Language]]:
        return None