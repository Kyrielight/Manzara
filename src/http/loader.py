
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

from src.commands.google import Google
from src.definitions.arguments_command import Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand

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

def _maybe_import_from_toml_file(root: str, file: str):
    """
    Helper to load a toml file into the lookup store.
    Do not use except in initialisation.
    """
    try:
        with open(join(root, file), 'r') as raw:
            modules = toml.load(raw)
            _maybe_import_from_file_modules(modules)
    except Exception as e:
        Ayumi.warning("Failed to load toml file under path {}".format(join(root, file)), color=Ayumi.LRED)

def _maybe_import_from_yaml_file(root: str, file: str):
    """
    Helper to load a yaml file into the lookup store.
    Do not use except in initialisation.
    """
    try:
        with open(join(root, file), 'r') as raw:
            modules = yaml.safe_load(raw)
            _maybe_import_from_file_modules(modules)
    except Exception as e:
        Ayumi.warning("Failed to load yaml file under path {}".format(join(root, file)), color=Ayumi.LRED)

def _load_commands_from_module(key: str, module: Dict) -> List[str]:
    """
    Loads triggers, slashes, etc. from a module file.
    """
    commands = module.get(key, list())
    if isinstance(commands, str):
       commands = [commands]
    return commands

def _maybe_import_from_file_modules(modules: Dict):

    # A single module/file can hold multiple definitions
    for name, module in modules.items():

        # Validate that each module at least fits the standard.
        if not MODULE_VALIDATOR.validate(module):
            Ayumi.warning("Module {} is invalid, skipping import.".format(name), color=Ayumi.RED)
            continue

        has_args = module['args']
        slashes = _load_commands_from_module("slashes", module)
        triggers = _load_commands_from_module("triggers", module)
        # Create a structure to store all urls with Language objects as keys
        language_lookup_dict: Dict[Language, str] = defaultdict(lambda: module['default'])

        # Load any locale-specific urls
        if 'urls' in module:
            for language, url in module['urls'].items():

                # If this is an args module, make sure there's a str to replace.
                if has_args and not "{arg}" in url:
                    Ayumi.warning("Module {} is set to accept arguments, but langcode {} doesn't accept arguments.".format(name, language))
                    continue

                try:
                    language_lookup_dict[Language.get(language)] = url
                except:
                    Ayumi.warning("Error importing language {} with url {}".format(language, url), color=Ayumi.LRED)
        # No locale-specific urls, only a default exists
        else:
            Ayumi.debug("No urls structure in module {}".format(name))

        # Create new lookup item
        lookup_item = LookupItem(lambda a, l: language_lookup_dict[l].format(arg=quote(' '.join(a[1:]))) \
                            if len(a) > 1 \
                            else language_lookup_dict.default_factory(),
                            list(language_lookup_dict.keys())) \
                        if has_args \
                            else LookupItem(lambda l: language_lookup_dict[l], list(language_lookup_dict.keys()))

        # Add bindings to lookups
        for trigger in triggers:
            Ayumi.debug("Adding trigger: {}".format(trigger), color=Ayumi.LCYAN)
            if trigger not in TRIGGER_LOOKUP:
                TRIGGER_LOOKUP[trigger] = lookup_item
            else:
                Ayumi.warning("Found duplicate trigger: {}".format(trigger), color=Ayumi.LYELLOW)

        for slash in slashes:
            Ayumi.debug("Adding slash: {}".format(slash), color=Ayumi.LCYAN)
            if slash.endswith("/"): slash = slash[:-1]
            if slash not in SLASH_LOOKUP:
                SLASH_LOOKUP[slash] = lookup_item
            else:
                Ayumi.warning("Found duplicate slash: {}".format(slash), color=Ayumi.LYELLOW)


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
for root, dirs, files in walk(("src/commands")):
    for file in files:
        Ayumi.debug("Now loading: {}".format(file))
        if file.endswith(".py"):
            _maybe_import_from_class_file(root, file)
        elif file.endswith(".toml"):
            _maybe_import_from_toml_file(root, file)
        elif file.endswith(".yaml") or file.endswith(".yml"):
            _maybe_import_from_yaml_file(root, file)
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