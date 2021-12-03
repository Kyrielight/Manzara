

import toml

from cerberus import Validator
from collections import defaultdict
from importlib import import_module
from inspect import getmembers, isclass
from os import walk
from os.path import join
from re import compile
from typing import Dict, List, Tuple
from urllib.parse import quote

from ayumi import Ayumi
from langcodes import Language

from src.commands.google import Google
from src.definitions.arguments_command import Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand

from .lookup_item import LookupItem

# Base classes and their programmatic names used for dynamic .py file imports
BASE_CLASSES = [Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand]
BASE_CLASS_NAMES = [x.__name__ for x in BASE_CLASSES]

TRIGGER_LOOKUP: Dict[str, LookupItem] = dict()
REGEX_LOOKUP: List[LookupError] = list()

MODULE_VALIDATOR = Validator({
    'args': {'type': 'boolean', 'required': True},
    'command': {'type': 'string', 'required': True},
    'default': {'type': 'string', 'required': True},
    'urls': {'type': 'dict', 'required': False}
})

# Lambda to determine if a dynamic class should be imported
should_import = lambda c : any([issubclass(c, x) for x in BASE_CLASSES]) and not any(c.__name__ == x for x in BASE_CLASS_NAMES)

def _maybe_import_from_class_file(root: str, file: str):
    """
    Helper to load a .py file into the lookup store.
    Do not use except in initialisation.
    """
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
                        Ayumi.debug("Adding trigger: {}".format(binding))
                        TRIGGER_LOOKUP[binding] = LookupItem(temp_instance.redirect, temp_instance.languages)
                for binding in temp_instance.bindings or list():
                    Ayumi.debug("Adding binding: {} with flag(s): {}".format(binding.pattern, binding.flags or "None"))
                    REGEX_LOOKUP.append((binding, LookupItem(temp_instance.redirect, temp_instance.languages)))

def _maybe_import_from_toml_file(root: str, file: str):
    """
    Helper to load a toml file into the lookup store.
    Do not use except in initialisation.
    """
    try:
        with open(join(root, file), 'r') as raw:
            modules = toml.load(raw)
            # A single file can hold multiple definitions
            for name, module in modules.items():

                # Validate that each module at least fits the standard.
                if not MODULE_VALIDATOR.validate(module):
                    Ayumi.warning("Module {} is invalid, skipping import.".format(name), color=Ayumi.RED)
                    continue

                # Only load commands that haven't been loaded before.
                if module['command'] in TRIGGER_LOOKUP:
                    Ayumi.warning("Module {} is reusing a command, skipping import.".format(name), color=Ayumi.RED)
                    continue

                has_args = module['args']
                binding = module['command']
                # Create a structure to store all urls with Language objects as keys
                lookup_dict: Dict[Language, str] = defaultdict(lambda: module['default'])

                # Load any locale-specific urls
                if 'urls' in module:
                    for language, url in module['urls'].items():

                        # If this is an args module, make sure there's a str to replace.
                        if has_args and not "{arg}" in url:
                            Ayumi.warning("Module {} is set to accept arguments, but langcode {} doesn't accept arguments.".format(name, language))
                            continue

                        try:
                            lookup_dict[Language.get(language)] = url
                        except:
                            Ayumi.warning("Error importing language {} with url {}".format(language, url), color=Ayumi.LRED)
                # No locale-specific urls, only a default exists
                else:
                    Ayumi.debug("No urls structure in module {}".format(name))

                # Add binding to the greater lookup
                if binding not in TRIGGER_LOOKUP:
                    Ayumi.debug("Adding trigger: {}".format(binding))
                    if has_args:
                        TRIGGER_LOOKUP[binding] = LookupItem(lambda a, l: lookup_dict[l].format(arg=quote(' '.join(a[1:]))) if len(a) > 1 \
                                                                            else lookup_dict.default_factory(), 
                                                                list(lookup_dict.keys()))
                    else:
                        TRIGGER_LOOKUP[binding] = LookupItem(lambda l: lookup_dict[l], list(lookup_dict.keys()))

    except Exception as e:
        Ayumi.warning("Failed to load toml file under path {}".format(join(root, file)), color=Ayumi.LRED)

def search(command: str, command_og: str, incognito: bool, language_accept: Tuple) -> str:
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

    # Fetch any module that this command matches. If not, Google is used by default.
    try:
        module = TRIGGER_LOOKUP[trigger]
        if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
    except:
        for binder in REGEX_LOOKUP:
            if binder[0].match(command):
                module = binder[1]
                if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
                break

    # Determine the language to be used, in accordance with support from the module.
    for la in language_accept:
        if la in module.languages:
            if not incognito: Ayumi.debug("Overwrote default language from en to {}".format(str(la)))
            language = la
            break

    # Return with command or without.
    try:
        url = module.redirect(language, command.split())
        if not incognito: Ayumi.debug('Returning "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
        return url
    except:
        url = module.redirect(language)
        if not incognito: Ayumi.debug('Returning "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
        return url

# Walk down the file and import modules.
for root, dirs, files in walk(("src/commands")):
    for file in files:
        if file.endswith(".py"):
            _maybe_import_from_class_file(root, file)
        elif file.endswith(".toml"):
            _maybe_import_from_toml_file(root, file)
        elif file.endswith(".yaml") or file.endswith(".yml"):
            pass

# We should default to Google if nothing else is matched
Ayumi.debug("Adding default Google redirection.")
REGEX_LOOKUP.append((compile(r'.*'), LookupItem(Google().redirect, Google().languages)))