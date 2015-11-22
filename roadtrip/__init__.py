__author__ = 'poojm'

from flask import Flask, render_template
from roadtrip.main.controllers import main
from roadtrip.main.helpers import generate_nonce
from roadtrip.api.controllers import api
from roadtrip.auth.auth import auth

app = Flask(__name__)
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(api, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')

app.jinja_env.globals['nonce'] = generate_nonce


@app.errorhandler(403)
def action_unauthorized(error):
    """Redirect the user to a site built 403 page"""
    return render_template('error_403.html', error=error), 403


@app.errorhandler(404)
def entity_not_found(error):
    """Redirect the user to a site built 404 page"""
    return render_template('error_404.html', error=error), 404
