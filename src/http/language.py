"""
Helper module for handling user locale
"""

import re

from ayumi import Ayumi

from collections import deque
from flask import request
from langcodes import DEFAULT_LANGUAGE, Language

from typing import Tuple

LANGUAGE_FINDER = re.compile(r'.*(( -.+ )|( -.+$))', re.IGNORECASE)

def get_languages(req: request, command: str) -> Tuple[Tuple[Language], str]:
    """
    Get the languages associated with this request, and return them as a Tuple.
    Also returns the new command with language codes removed, if applicable.
    """

    languages = deque()

    # If user has set a language override, set that as the primary language.
    try:
        override_lang = req.args['language']
        languages.appendleft(Language.get(override_lang))
        Ayumi.debug("Detected user language override in params: {}".format(override_lang))
    except:
        Ayumi.debug("Did not detect user language override from request parameters")

    # Fetch the languages the user's browser provided as part of the accept and convert them to Language objects
    languages.extend(Language.get(l) for l in sorted(
                            req.accept_languages.values(),
                            key=lambda v: req.accept_languages.quality(v),
                            reverse=True))
    Ayumi.debug("Detected browser language: {}".format(req.accept_languages.to_header()))

    if match := LANGUAGE_FINDER.search(command):
        override_lang = match.groups()[0].strip()[1:]
        languages.appendleft(Language.get(override_lang))
        Ayumi.debug("Detected user language override: {}".format(override_lang))
        command = command.replace(match.groups()[0], " ").strip()
        Ayumi.debug("Removed language codes, new command: \"{}\"".format(command))
    else:
        Ayumi.debug("No user command language overrides detected.")

    Ayumi.debug("Returning language priority list: {}".format(languages))
    return tuple(languages), command



