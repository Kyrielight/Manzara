import re

from langcodes import Language
from src.commands.arguments_command import Usagi12WithArgumentsCommand
from typing import Optional, Tuple
from urllib.parse import quote

YOUTUBE_URL_BASE = "https://youtube.com"
YOUTUBE_URL_SEARCH = "https://youtube.com/results?search_query={query}"

class Youtube(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str], language: Optional[Language]) -> str:
        if len(args) > 1:
            return YOUTUBE_URL_SEARCH.format(query=quote(' '.join(args[1:])))
        else:
            return YOUTUBE_URL_BASE
    
    @property
    def description(self) -> str:
        return """For making searches on YouTube"""
    
    @property
    def bindings(self) -> Optional[Tuple[re.Pattern]]:
        return None
    
    @property
    def slashes(self) -> Optional[Tuple[str]]:
        return None

    @property
    def triggers(self) -> Optional[Tuple[str]]:
        return (
            "yt",
            "youtube",
        )
    
    @property
    def languages(self) -> Optional[Tuple[Language]]:
        return None