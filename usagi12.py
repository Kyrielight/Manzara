import logging

from ayumi import Ayumi

from flask import Flask, request, redirect
from langcodes import DEFAULT_LANGUAGE, Language

from commands.google import Google # Default fallback
from src.http import language as language_helper
from src.athenaeum import loader


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
        Ayumi.debug("Received user command: {}".format(command))

        # Fetch the language used for the request
        language_accept, command = language_helper.get_languages(request, command)
        Ayumi.debug("Got languages: {}".format([x._str_tag for x in language_accept]))

        url = loader.search(command, command_og, tuple(language_accept))
        Ayumi.info('Redirecting "{}" to "{}'.format(command_og, url), color=Ayumi.LCYAN)
        return redirect(url)
        
    except Exception as e:
        url = Google().redirect((), Language.get(DEFAULT_LANGUAGE))
        Ayumi.warning("Caught error: {}, redirecting query to default: {}".format(e, url), Ayumi.LRED)
        return redirect(url)

if __name__ == "__main__":
    Ayumi.info("Now starting Usagi12 server in Flask debug mode", color=Ayumi.GREEN)
    app.run(host='0.0.0.0', port=6973, debug=True)