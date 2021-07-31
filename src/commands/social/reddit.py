import re

from src.definitions.arguments_command import Usagi12WithArgumentsCommand
from typing import Optional, Tuple
from urllib.parse import quote

REDDIT_URL_BASE = "https://reddit.com/"
REDDIT_URL_SUBREDDIT = REDDIT_URL_BASE + "r/{}"
REDDIT_URL_SEARCH= REDDIT_URL_BASE + "search?q={}{}"

NSFW_FLAG = "&include_over_18=on"

class Reddit(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str]) -> str:
        if len(args) == 1 and args[0].startswith("r/"):
            return REDDIT_URL_SUBREDDIT.format(quote(args[0][2:]))
        else:
            if len(args) > 1:
                nsfw = True if "18" in args[0] or "nsfw" in args[0] else False
                return REDDIT_URL_SEARCH.format(" ".join(args[1:]), NSFW_FLAG if nsfw else str())
            else:
                return REDDIT_URL_BASE

    @property
    def description(self) -> str:
        return """For making searches or navigating through Reddit"""
    
    @property
    def bindings(self) -> Optional[Tuple[re.Pattern]]:
        return (
            re.compile(r'^(?:r\/\w+)|(?:re?((?:18)|(?:nsfw))? .+)$'),
        )
    
    @property
    def triggers(self) -> Optional[Tuple[str]]:
        return None