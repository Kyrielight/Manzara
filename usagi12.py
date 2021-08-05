import logging
import re

from ayumi import Ayumi

from collections import deque
from flask import Flask, request, redirect
from langcodes import DEFAULT_LANGUAGE, Language

from src.commands.google import Google # Default fallback
from src.http.lookup_store import LookupStore


INCOGNITO_BINDING = re.compile(r'^((?:!)|(?:incognito)|(?:incog)|(?:nolog))(?:\s?)', re.IGNORECASE)
LANGUAGE_OVERRIDE_BINDING = re.compile(r'(?:^(?:(?:in:([\w-]+))|(?:\.([\w-]+))(?!.+-[\w-]+$))(?:\s?))|(?:\ -([\w-]+)$)', re.IGNORECASE)

app = Flask(__name__)
# Disable Werkzeug logger to respect incognito settings.
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

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

        return redirect(LookupStore.search(command, command_og, incognito, language_accept))

        
    except Exception:
        url = Google().redirect((), Language.get(DEFAULT_LANGUAGE))
        if not incognito: Ayumi.info('No match found, redirecting to default: {}'.format(url), color=Ayumi.LBLUE)
        return redirect(url)

if __name__ == "__main__":
    Ayumi.info("Now starting Usagi12 server via Flask Dev...", color=Ayumi.GREEN)
    app.run(host='0.0.0.0', port=6973)