import importlib
import inspect
import logging
import os
import re

from ayumi import Ayumi
from werkzeug.datastructures import LanguageAccept

from src.definitions.arguments_command import Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand
from typing import Callable, Dict, List, Tuple

from collections import deque
from flask import Flask, request, redirect
from langcodes import DEFAULT_LANGUAGE, Language
from urllib.parse import quote

from src.commands.google import Google # Default fallback

class LookupItem:

    def __init__(self, redirect: Callable, languages: Tuple[Language]):
        self._redirect: Callable = redirect
        self._languages: Tuple[Language] = languages
    
    def redirect(self, *args: Tuple[str]) -> str:
        try:
            return self._redirect(args[0])
        except:
            return self._redirect()
     
    @property
    def languages(self) -> Tuple[Language]:
        return self._languages           


BASE_CLASSES = [Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand]
BASE_CLASS_NAMES = [x.__name__ for x in BASE_CLASSES]

LOOKUP_DICT: Dict[str, Callable] = dict()
LOOKUP_REGEX_LIST: List[Tuple[re.Pattern, Callable]] = list() # Iterate through to find first matching regex.

TRIGGER_LOOKUP: Dict[str, LookupItem] = dict()
REGEX_LOOKUP: List[LookupItem] = list()

INCOGNITO_BINDING = re.compile(r'^((?:!)|(?:incognito)|(?:incog)|(?:nolog))(?:\s?)', re.IGNORECASE)

LANGUAGE_OVERRIDE_BINDING = re.compile(r'(?:^(?:(?:in:([\w-]+))|(?:\.([\w-]+))(?!.+-[\w-]+$))(?:\s?))|(?:\ -([\w-]+)$)', re.IGNORECASE)

app = Flask(__name__)
# Disable Werkzeug logger to respect incognito settings.
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

"""
Some preprocessing steps:

1. Dynamically import every subcommand module.
2. If we want to use it, then create an instance of the class, and attach its bindings to the lookup dictionary.

Keep in mind this is not really a safe loader, but this strapping occurs before any public input.
Merge requests, etc. should be very carefully verified (if anyone even uses this lol).
-- I'm just too lazy to want to manually manage this :)
"""
# Create a helper to validate eligibility of import. Maybe move this to util later on.
should_import = lambda c : any([issubclass(c, x) for x in BASE_CLASSES]) and not any(c.__name__ == x for x in BASE_CLASS_NAMES)
for root, dirs, files in os.walk(("src/commands")):
    for file in files:
        if file.endswith(".py"):
            # Import any file that ends with .py
            mod_path = os.path.join(root, file).replace("/", ".")[:-3]
            module = importlib.import_module(mod_path)
            if module:
                classes = [x for x in inspect.getmembers(module, inspect.isclass)]
                for c in classes:
                    # Only import modules that are in a specific subclass that we want to work with
                    if should_import(c[1]):
                        # ----------- #
                        temp_instance = c[1]() # Create an instance of the class
                        Ayumi.debug("Loading class: {}".format(temp_instance.__class__.__name__))
                        for binding in temp_instance.triggers or list():
                            if binding not in LOOKUP_DICT:
                                Ayumi.debug("Adding trigger: {}".format(binding))
                                LOOKUP_DICT[binding] = temp_instance.redirect
                            else:
                                Ayumi.warning("Duplicate trigger found: {}".format(binding), color=Ayumi.RED)
                        for binding in temp_instance.bindings or list():
                            Ayumi.debug("Adding binding: {} with flag(s): {}".format(binding.pattern, binding.flags or "None"))
                            LOOKUP_REGEX_LIST.append((binding, temp_instance.redirect))
                        # ----------- #
                        for binding in temp_instance.triggers or list():
                            if binding not in TRIGGER_LOOKUP:
                                Ayumi.debug("Adding trigger: {}".format(binding))
                                TRIGGER_LOOKUP[binding] = LookupItem(temp_instance.redirect, temp_instance.languages)
                        for binding in temp_instance.bindings or list():
                            Ayumi.debug("Adding binding: {} with flag(s): {}".format(binding.pattern, binding.flags or "None"))
                            REGEX_LOOKUP.append((binding, LookupItem(temp_instance.redirect, temp_instance.languages)))

# We should default to Google if nothing else is matched
Ayumi.debug("Adding default Google redirection.")
LOOKUP_REGEX_LIST.append((re.compile(r'.*'), Google().redirect))
REGEX_LOOKUP.append((re.compile(r'.*'), LookupItem(Google().redirect, Google().languages)))

print(REGEX_LOOKUP)


@app.route("/bunny", methods=['GET'])
def bunny():
    try:
        if 'query' not in request.args or not request.args['query']:
            raise Exception()

        command = request.args['query'].strip()
        
        # Special binding that can allow incognito search (no-log)
        incognito = INCOGNITO_BINDING.match(command) != None
        if incognito: command = INCOGNITO_BINDING.sub("", command)

        # Fetch the language to use for the request
        language_accept = deque(Language(l) for l in request.accept_languages.values())
        if not incognito: Ayumi.debug("Detected browser language: {}".format(request.accept_languages.to_header()))
        # Load any user overrides, if specified
        if match := LANGUAGE_OVERRIDE_BINDING.search(command): 
            language_accept.appendleft(Language(next(lang for lang in match.groups() if lang is not None)))
            if not incognito: Ayumi.debug("User provided language override: {}".format(str(language_accept[0])))
            command = LANGUAGE_OVERRIDE_BINDING.sub("", command)
        
        trigger = command.split()[0]
        language: LanguageAccept = Language.get(DEFAULT_LANGUAGE)

        # First check if a trigger exists for our command, more efficient
        try:
            module: LookupItem = TRIGGER_LOOKUP[trigger]
            if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
            for la in language_accept:
                if la in (module.languages or list()):
                    if not incognito: Ayumi.debug("Overwrote default language from en to {}".format(str(la)))
                    language = la
                    break
            try:
                url = module.redirect(command.split())
                if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command, url), color=Ayumi.LCYAN)
                return redirect(url)
            except:
                url = module.redirect()
                if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command, url), color=Ayumi.LCYAN)
                return redirect(url)
        # No amtch, so we'll need to scan all the regexes for a potential match.
        except:
            for binder in REGEX_LOOKUP:
                if binder[0].match(command):
                    module = binder[1]
                    if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
                    for la in language_accept:
                        if la in (module.languages or list()):
                            if not incognito: Ayumi.debug("Overwrote default language from en to {}".format(str(la)))
                            language = la
                            break
                    try:
                        url = module.redirect(command.split())
                        if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command, url), color=Ayumi.LCYAN)
                        return redirect(url)
                    except:
                        url = module.redirect()
                        if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command, url), color=Ayumi.LCYAN)
                        return redirect(url)
    except Exception:
        url = Google().redirect(())
        if not incognito: Ayumi.info('No match found, redirecting to default: {}'.format(url), color=Ayumi.LBLUE)
        return redirect(url)

if __name__ == "__main__":
    Ayumi.info("Now starting Usagi12 server via Flask Dev...", color=Ayumi.GREEN)
    app.run(host='0.0.0.0', port=6973)