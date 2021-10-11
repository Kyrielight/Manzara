"""
Helper module for handling user locale
"""

from ayumi import Ayumi

from collections import deque
from flask import request
from langcodes import DEFAULT_LANGUAGE, Language

from typing import Tuple

def get_languages(req: request, command: str, incognito: bool) -> Tuple[Tuple[Language], str]:
    """
    Get the languages associated with this request, and return them as a Tuple.
    Also returns the new command with language codes removed, if applicable.
    """

    languages = deque()

    # If user has set a language override, set that as the primary language.
    try:
        override_lang = request.args['language']
        languages.append(Language.get(override_lang))
        if not incognito:
            Ayumi.debug("Detected user language override in params: {}".format(override_lang))
    except:
        pass

    # Fetch the languages the user's browser provided as part of the accept and convert them to Language objects
    languages.extend(Language.get(l) for l in sorted(
                            request.accept_languages.values(),
                            key=lambda v: request.accept_languages.quality(v),
                            reverse=True))
    if not incognito: 
        Ayumi.debug("Detected browser language: {}".format(request.accept_languages.to_header()))

    # If user has provided an override themselves, that takes precedent
    command_split = command.split()
    try:
        manual_lang = command_split[1].replace(":", "-")

        if manual_lang.startswith("-"):
            # Add language as primary
            languages.appendleft(Language.get(manual_lang[1:]))
            if not incognito:
                Ayumi.debug("Detected user language override: {}".format(manual_lang[1:]))
            # Remove that override from the command 
            command_split.pop(1)

        elif manual_lang.startswith("\-"):
            # Literal hyphen
            command_split[1] = command_split[1][1:]
            if not incognito:
                Ayumi.debug("Detected literal hyphen, removing from command.")
    except:
        pass

    if not incognito:
        Ayumi.debug("Returning language priority list: {}".format(languages))
    return tuple(languages), " ".join(command_split)



