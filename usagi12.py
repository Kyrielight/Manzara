import importlib
import inspect
import logging
import os
import re

from ayumi import Ayumi

from src.definitions.arguments_command import Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand
from typing import Callable, Dict, Optional, List, Tuple

from collections import deque
from flask import Flask, request, redirect
from langcodes import DEFAULT_LANGUAGE, Language

from src.commands.google import Google # Default fallback
from src.http.lookup_item import LookupItem

BASE_CLASSES = [Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand]
BASE_CLASS_NAMES = [x.__name__ for x in BASE_CLASSES]

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
REGEX_LOOKUP.append((re.compile(r'.*'), LookupItem(Google().redirect, Google().languages)))

@app.route("/bunny", methods=['GET'])
def bunny():
    try:
        if 'query' not in request.args or not request.args['query']:
            raise Exception()

        # Make a copy of the command for modification, and store original for logging
        command = command_og = request.args['query'].strip()

        # Special binding that can allow incognito search (no-log)
        incognito = (request.args.get("incognito", "false").lower() == "true") or (INCOGNITO_BINDING.match(command) != None)
        if incognito: command = INCOGNITO_BINDING.sub("", command)
        if not incognito: Ayumi.debug("User command: {}".format(command))

        # Fetch the languages the user's browser provided as part of the accept and convert them to Language objects
        language_accept = deque(Language.get(l) for l in sorted(
                                request.accept_languages.values(),
                                key=lambda v: request.accept_languages.quality(v),
                                reverse=True)
                            )
        if not incognito: Ayumi.debug("Detected browser language: {}".format(request.accept_languages.to_header()))

        # If the user specified an override language, add that to the foremost of the accepted to give it highest priority.
        if match := LANGUAGE_OVERRIDE_BINDING.search(command):
            language_accept.appendleft(Language.get(next(lang for lang in match.groups() if lang is not None)))
            if not incognito: Ayumi.debug("User provided language override: {}".format(str(language_accept[0])))
            command = LANGUAGE_OVERRIDE_BINDING.sub("", command)

        # To preserve the null state, the default language is None (if not provided).
        # This will be passed to the module if the module does not support any languages forwarded by the user's browser.
        language: Language = None

        # If there is a trigger word, it would be the first word at this stage.
        trigger = command.split()[0]

        # First check if a trigger exists for our command, more efficient
        try:
            module: LookupItem = TRIGGER_LOOKUP[trigger]
            if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
            for la in language_accept:
                if la in module.languages:
                    if not incognito: Ayumi.debug("Overwrote default language from en to {}".format(str(la)))
                    language = la
                    break
            try:
                url = module.redirect(language, command.split())
                if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
                return redirect(url)
            except:
                url = module.redirect(language)
                if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
                return redirect(url)
        # No amtch, so we'll need to scan all the regexes for a potential match.
        except:
            for binder in REGEX_LOOKUP:
                if binder[0].match(command):
                    module = binder[1]
                    if not incognito: Ayumi.debug("Loaded module declared languages: {}".format(module.languages))
                    for la in language_accept:
                        if la in module.languages:
                            if not incognito: Ayumi.debug("Overwrote default language from en to {}".format(str(la)))
                            language = la
                            break
                    try:
                        url = module.redirect(language, command.split())
                        if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
                        return redirect(url)
                    except:
                        url = module.redirect(language)
                        if not incognito: Ayumi.info('Redirecting "{}" to "{}"'.format(command_og, url), color=Ayumi.LCYAN)
                        return redirect(url)
    except Exception:
        url = Google().redirect((), Language.get(DEFAULT_LANGUAGE))
        if not incognito: Ayumi.info('No match found, redirecting to default: {}'.format(url), color=Ayumi.LBLUE)
        return redirect(url)

if __name__ == "__main__":
    Ayumi.info("Now starting Usagi12 server via Flask Dev...", color=Ayumi.GREEN)
    app.run(host='0.0.0.0', port=6973)