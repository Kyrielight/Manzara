
from cerberus import Validator
from importlib import import_module
from inspect import getmembers, isclass
from os import walk
from os.path import join
from re import compile
from typing import Dict, List

from ayumi import Ayumi

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