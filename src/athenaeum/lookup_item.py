from langcodes import Language
from typing import Callable, Optional, Tuple

class LookupItem:

    def __init__(self, redirect: Callable, languages: Optional[Tuple[Language]]):
        self._redirect: Callable = redirect
        self._languages: Tuple[Language] = languages or tuple()

    def redirect(self, language: Optional[Language], *args: Tuple[str]) -> str:
        try:
            return self._redirect(args[0], language)
        except:
            return self._redirect(language)

    @property
    def languages(self) -> Tuple[Language]:
        return self._languages