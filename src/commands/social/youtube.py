import re

from definitions.arguments_command import Usagi12WithArgumentsCommand
from typing import Tuple
from urllib.parse import quote

YOUTUBE_URL_BASE = "https://youtube.com"
YOUTUBE_URL_SEARCH = "https://youtube.com/results?search_query={query}"

class Youtube(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str]) -> str:
        if len(args) > 1:
            return YOUTUBE_URL_SEARCH.format(query=quote(' '.join(args[1:])))
        else:
            return YOUTUBE_URL_BASE
    
    @property
    def description(self) -> str:
        return """For making searches on YouTube"""
    
    @property
    def bindings(self) -> Tuple[re.Pattern]:
        return None
    
    @property
    def triggers(self) -> Tuple[str]:
        return (
            "yt",
            "youtube",
        )