"""
Helper module for handling the "incognito" feature for Usagi12.
"""

from flask import request


def is_enabled(query: str, req: request):
    """Returns if incognito mode is enabled or not."""
    return request.args.get("incognito", "false").lower() == "true" or query.startswith("!")

def get_new_command(command: str):
    """Returns new command, stripped of incognito flags."""
    if command.startswith("!"):
        return command[1:]
    else:
        return command #Remove ! at the beginning.
