from collections import deque
from importlib import import_module
from inspect import getmembers, isclass
from os import walk
from os.path import join
from re import compile
from typing import Dict, List

from ayumi import Ayumi
from langcodes import Language

from src.commands.google import Google # Default fallback
from src.definitions.arguments_command import Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand

from .lookup_item import LookupItem

BASE_CLASSES = [Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand]
BASE_CLASS_NAMES = [x.__name__ for x in BASE_CLASSES]

class LookupStore:

    # Import all relevant modules on class initialisation.
    # Note that context is run from the root file's location.
    TRIGGER_LOOKUP: Dict[str, LookupItem] = dict()
    REGEX_LOOKUP: List[LookupItem] = list()

    should_import = lambda c : any([issubclass(c, x) for x in BASE_CLASSES]) and not any(c.__name__ == x for x in BASE_CLASS_NAMES)
    for root, dirs, files in walk(("src/commands")):
        for file in files:
            if file.endswith(".py"):
                # Import any file that ends with .py
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

    # We should default to Google if nothing else is matched
    Ayumi.debug("Adding default Google redirection.")
    REGEX_LOOKUP.append((compile(r'.*'), LookupItem(Google().redirect, Google().languages)))

    @classmethod
    def search(cls, command: str, command_og: str, incognito: bool, language_accept: deque) -> str:
        """
        Perform a search over imported modules and return the best match. Defaults to Google.

        Params:
        - command: Formatted command string after modifications to search.
        - command_og: Original command, used for logging purposes.
        - incognito: Whether or not to store logging data
        - language_accept: A deque of Language objects to check for the best language.
        """

        module: LookupItem = LookupItem(Google().redirect, Google().languages)
        language: Language = None

        # If there is a trigger word, it would be the first word in the command
        trigger = command.split()[0]

        # Fetch any module that this command matches. If not, Google is used by default.
        try:
            module = cls.TRIGGER_LOOKUP[trigger]
            if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
        except:
            for binder in cls.REGEX_LOOKUP:
                if binder[0].match(command):
                    module = binder[1]
                    if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
        
        # Determine the language to be used, in accordance with support from the module.
        for la in language_accept:
            if la in module.languages:
                if not incognito: Ayumi.debug("Overwrote default language from en to {}".format(str(la)))
                language = la
                break
    
        # Return with command or without.
        try:
            url = module.redirect(language, command.split())
            if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
            return url
        except:
            url = module.redirect(language)
            if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
            return url            