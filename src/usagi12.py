import importlib
import inspect
import os
import re

from definitions.arguments_command import Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand
from typing import Callable, Dict, List, Tuple

from flask import Flask, request, redirect
from urllib.parse import quote

from commands.google import Google # Default fallback

BASE_CLASSES = [Usagi12WithArgumentsCommand, Usagi12WithoutArgumentsCommand]
BASE_CLASS_NAMES = [x.__name__ for x in BASE_CLASSES]
LOOKUP_REGEX_LIST: List[Tuple[re.Pattern, Callable]] = list() # Iterate through to find first matching regex.
LOOKUP_DICT: Dict[str, Callable] = dict()

app = Flask(__name__)

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
for root, dirs, files in os.walk(("commands")):
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
                            if binding not in LOOKUP_DICT:
                                LOOKUP_DICT[binding] = temp_instance.redirect
                            else:
                                # TODO: Migrate to Ayumi for logging
                                print("Warning: Duplicate trigger found: {}".format(binding))
                        for binding in temp_instance.bindings or list():
                            LOOKUP_REGEX_LIST.append((binding, temp_instance.redirect))

# We should default to Google if nothing else is matched
LOOKUP_REGEX_LIST.append((re.compile(r'.*'), Google().redirect))


@app.route("/bunny", methods=['GET'])
def bunny():
    try:
        if 'query' not in request.args or not request.args['query']:
            raise Exception()

        command = request.args['query'].strip()
        trigger = command.split()[0]
        
        if trigger in LOOKUP_DICT:
            try:
                return redirect(LOOKUP_DICT[trigger](command.split()))
            except:
                return redirect(LOOKUP_DICT[trigger]())
        else:
            for binder in LOOKUP_REGEX_LIST:
                if binder[0].match(command):
                    try:
                        return redirect(binder[1](command.split()))
                    except:
                        return redirect(binder[1]())

    except:
        return redirect(Google().redirect([]))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6973)