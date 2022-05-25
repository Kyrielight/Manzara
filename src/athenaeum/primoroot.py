
from .loader import TRIGGER_LOOKUP, SLASH_LOOKUP, REGEX_LOOKUP
from .lookup_item import LookupItem

from ayumi import Ayumi
from commands.google import Google
from enum import Enum
from langcodes import Language
from typing import Tuple

class CommandMode(Enum):
    TRIGGER = 1
    SLASH = 2
    REGEX = 3

def search(command: str, command_og: str, language_accept: Tuple) -> str:
    """
    Perform a search over imported modules and return the best match. Defaults to Google.

    Params:
    - command: Formatted command string after modifications to search.
    - command_og: Original command, used for logging purposes.
    - incognito: Whether or not to store logging data
    - language_accept: A Tuple of Language objects to check for the best language.
    """

    module: LookupItem = LookupItem(Google().redirect, Google().languages)
    language: Language = None

    # If there is a trigger word, it would be the first word in the command
    trigger = command.split()[0]
    # If the command is a slah command, the trigger would have '/' in it.
    slash = trigger.split('/')[0] if '/' in trigger else None

    # Fetch any module that this command matches. If not, Google is used by default.
    command_type = None
    try:
        module = TRIGGER_LOOKUP[trigger]
        command_type = CommandMode.TRIGGER
        Ayumi.debug("Found in trigger lookup: {}".format(trigger))
    except:
        try:
            module = SLASH_LOOKUP[slash]
            command_type = CommandMode.SLASH
            Ayumi.debug("Found in slash lookup: {}".format(slash))
        except:
            for binder in REGEX_LOOKUP:
                if binder[0].match(command):
                    module = binder[1]
                    command_type = CommandMode.REGEX
                    Ayumi.debug("Matched in regex lookup: {}".format(command))
                    break

    # Determine the language to be used, in accordance with support from the module.
    Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
    for la in language_accept:
        if la in [Language.get(i) for i in module.languages]:
            Ayumi.debug("Overwrote request use language from en to {}".format(str(la)))
            language = la
            break

    # Return with command or without.
    try:
        # For ease of development, just convert the slash command into a trigger command.
        url = module.redirect(language, command.replace("/", " ").split()) \
            if command_type is CommandMode.SLASH \
            else module.redirect(language, command.split())
        Ayumi.debug('Returning "{}" to "{}"'.format(command_og, url))
        return url
    except:
        url = module.redirect(language)
        Ayumi.debug('Returning "{}" to "{}"'.format(command_og, url))
        return url
