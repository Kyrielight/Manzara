import re

from definitions.arguments_command import Usagi12WithArgumentsCommand
from typing import Tuple
from urllib.parse import quote

TWITTER_URL_BASE = "https://twitter.com/"
TWITTER_URL_SEARCH = "https://www.twitter.com/search?q="

class Twitter(Usagi12WithArgumentsCommand):

    def redirect(self, args: Tuple[str]) -> str:
        if len(args) > 1:

            root_arg = args[0].lower()

            if root_arg == "t@":
                return TWITTER_URL_BASE + args[1]
            else:
                return TWITTER_URL_SEARCH + quote(' '.join(args[1:]))

        else:
            return 'https://www.twitter.com'

    @property
    def description(self) -> str:
        return """For making searches on Twitter"""

    @property
    def bindings(self) -> Tuple[re.Pattern]:
        return (
            re.compile(r'^(?:t@|t|twitter)(?:\ .+)?$', re.IGNORECASE),
        )

    @property
    def triggers(self) -> Tuple[str]:
        return (
            "t",
            "twitter"
        )