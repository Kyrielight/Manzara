
import toml
import yaml

from cerberus import Validator
from collections import defaultdict
from enum import Enum
from importlib import import_module
from inspect import getmembers, isclass
from os import walk
from os.path import join
from re import compile
from typing import Dict, List, Tuple
from urllib.parse import quote

from ayumi import Ayumi
from langcodes import Language

from commands.google import Google
from src.commands.arguments_command import Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand

from .lookup_item import LookupItem

# Base classes and their programmatic names used for dynamic .py file imports
BASE_CLASSES = [Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand]
BASE_CLASS_NAMES = [x.__name__ for x in BASE_CLASSES]

TRIGGER_LOOKUP: Dict[str, LookupItem] = dict()
SLASH_LOOKUP: Dict[str, LookupItem] = dict()
REGEX_LOOKUP: List[LookupError] = list()

MODULE_VALIDATOR = Validator({
    'args': {'type': 'boolean', 'required': True},
    'description': {'type': 'string', 'required': True},
    'default': {'type': 'string', 'required': True},
    'slashes': {'type': ['string', 'list'], 'schema': {'type': 'string'}, 'required': False},
    'triggers': {'type': ['string', 'list'], 'schema': {'type': 'string'}, 'required': False},
    'urls': {'type': 'dict', 'required': False},
})

class CommandMode(Enum):
    TRIGGER = 1
    SLASH = 2
    REGEX = 3


def _maybe_import_from_class_file(root: str, file: str):
    """
    Helper to load a .py file into the lookup store.
    Do not use except in initialisation.
    """

    if (file == "__init__.py"):
        Ayumi.debug("Found __init__.py file, skipping.")
        return

    # Lambda to determine if a dynamic class should be imported
    should_import = lambda c : any([issubclass(c, x) for x in BASE_CLASSES]) and not any(c.__name__ == x for x in BASE_CLASS_NAMES)

    mod_path = join(root, file).replace("/", ".")[:-3]
    module = import_module(mod_path)
    if module:
        classes = [x for x in getmembers(module, isclass)]
        for c in classes:
            # Only import modules that are in a specific subclass that we want to work with
            if should_import(c[1]):
                temp_instance = c[1]() # Create an instance of the class
                for binding in temp_instance.triggers or list():
                    if binding not in TRIGGER_LOOKUP:
                        Ayumi.debug("Adding trigger: {}".format(binding), color=Ayumi.LCYAN)
                        TRIGGER_LOOKUP[binding] = LookupItem(temp_instance.redirect, temp_instance.languages)
                for binding in temp_instance.slashes or list():
                    if binding.endswith("/"): binding = binding[:-1]
                    if binding not in SLASH_LOOKUP:
                        Ayumi.debug("Adding slash: {}".format(binding), color=Ayumi.LCYAN)
                        SLASH_LOOKUP[binding] = LookupItem(temp_instance.redirect, temp_instance.languages)
                for binding in temp_instance.bindings or list():
                    Ayumi.debug("Adding binding: {} with flag(s): {}".format(binding.pattern, binding.flags or "None"), color=Ayumi.LCYAN)
                    REGEX_LOOKUP.append((binding, LookupItem(temp_instance.redirect, temp_instance.languages)))

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

# Walk down the file and import modules.
Ayumi.debug("Starting module import process...", color=Ayumi.BLUE)
for root, dirs, files in walk(("commands")):
    for file in files:
        Ayumi.debug("Now loading: {}".format(file))
        if file.endswith(".py"):
            _maybe_import_from_class_file(root, file)
        elif file.endswith(".pyc"):
            Ayumi.debug("Found bytecode file: {}, skipping...".format(file))
        else:
            Ayumi.debug("Unrecognised/unimplemented file type: {}, skipping...".format(file), color=Ayumi.LYELLOW)
        Ayumi.debug("Completed loading: {}".format(file))

# We should default to Google if nothing else is matched
Ayumi.debug("Adding default Google redirection.", color=Ayumi.LCYAN)
REGEX_LOOKUP.append((compile(r'.*'), LookupItem(Google().redirect, Google().languages)))

Ayumi.debug("Loading complete.", color=Ayumi.BLUE)
Ayumi.debug("Stats: Loaded triggers: {}".format(len(TRIGGER_LOOKUP)), color=Ayumi.MAGENTA)
Ayumi.debug("Stats: Loaded slashes: {}".format(len(SLASH_LOOKUP)), color=Ayumi.MAGENTA)
Ayumi.debug("Stats: Loaded regexes: {}".format(len(REGEX_LOOKUP)), color=Ayumi.MAGENTA)