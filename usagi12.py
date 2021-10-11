import logging
import re

from ayumi import Ayumi

from collections import deque
from flask import Flask, request, redirect
from langcodes import DEFAULT_LANGUAGE, Language

from src.commands.google import Google # Default fallback
from src.http import incognito as incognito_helper, language as language_helper
from src.http.lookup_store import LookupStore


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
        incognito = incognito_helper.is_enabled(command, request)
        if incognito: command = incognito_helper.get_new_command(command)
        else: Ayumi.debug("User command: {}".format(command))

        language_accept, command = language_helper.get_languages(request, command, incognito)

        url = LookupStore.search(command, command_og, incognito, tuple(language_accept))
        if not incognito: Ayumi.info('Redirecting "{}" to "{}'.format(command_og, url), color=Ayumi.LCYAN)
        return redirect(url)
        
    except Exception as e:
        if not incognito: Ayumi.warning("Caught error: {}".format(e), Ayumi.LRED)
        url = Google().redirect((), Language.get(DEFAULT_LANGUAGE))
        if not incognito: Ayumi.info('No match found, redirecting to default: {}'.format(url), color=Ayumi.LBLUE)
        return redirect(url)

if __name__ == "__main__":
    Ayumi.info("Now starting Usagi12 server via Flask Dev...", color=Ayumi.GREEN)
    app.run(host='0.0.0.0', port=6973, debug=True)