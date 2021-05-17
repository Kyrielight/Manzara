import importlib
import inspect
import os
import re

from definitions.arguments_command import ManzaraWithArgumentsCommand
from typing import Callable, List, Tuple

BASE_CLASSES = [ManzaraWithArgumentsCommand]
BASE_CLASS_NAMES = [x.__name__ for x in BASE_CLASSES]
LOOKUP_LIST: List[Tuple[re.Pattern, Callable]] = list() # Iterate through to find first matching regex.

def should_import_class(c):
    return any([issubclass(c, x) for x in BASE_CLASSES]) \
           and not any(c.__name__ == x for x in BASE_CLASS_NAMES)

"""
Some preprocessing steps:

1. Dynamically import every subcommand module.
2. If we want to use it, then create an instance of the class, and attach its bindings to the lookup dictionary.
"""
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
                    if should_import_class(c[1]):
                        temp_instance = c[1]() # Create an instance of the class
                        for binding in temp_instance.bindings:
                            LOOKUP_LIST.append((binding, temp_instance.redirect))

print(LOOKUP_LIST)