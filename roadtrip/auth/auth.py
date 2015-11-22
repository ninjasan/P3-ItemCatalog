__author__ = 'poojm'

import json
import httplib2
import requests

from flask import Flask, url_for, request, redirect, make_response, Blueprint
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from roadtrip.main.helpers import create_user, get_user_info, get_user_id


auth = Blueprint('auth', __name__, template_folder='templates')

CLIENT_ID = json.loads(open('roadtrip/auth/client_secret.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Roadtrip Catalog App"


@auth.route('gconnect', methods=['POST'])
def gconnect():
    """Provides functionality to login the user via their Google account"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Connect-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data

    try:
        # turn the auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('roadtrip/auth/client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code'), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}'.
           format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there was an error int he access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user Id doesn't match the given user ID."),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that that access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's"),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps("Current user is already connected."),
            200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # store access token in the session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # get user info (to prove you can)
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # see if user exists
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    return output


@auth.route('fbconnect', methods=['POST'])
def fbconnect():
    """Provides functionality to login the user via their Facebook account"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('roadtrip/auth/fb_client_secrets.json',
                             'r').read())['web']['app_id']
    app_secret = json.loads(open('roadtrip/auth/fb_client_secrets.json',
                                 'r').read())['web']['app_secret']
    url = "https://graph.facebook.com/oauth/access_token?" \
          "grant_type=fb_exchange_token&" \
          "client_id={0}&" \
          "client_secret={1}&" \
          "fb_exchange_token={2}".format(app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.4/me'
    # strip expire tag from access token
    token = result.split('&')[0]

    url = "https://graph.facebook.com/v2.4/me?{0}&fields=name,id,email".\
          format(token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # the token must be stored in the login_session in order to properly logout.
    # let's strip out the information before the equals in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # get the user pic
    url = "https://graph.facebook.com/v2.4/me/picture?{0}" \
          "&redirect=0&height=200&width=200".format(token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    return output


@auth.route('disconnect')
def disconnect():
    """Provides general logout clean-up for the session"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('main.list_cities'))
    else:
        return redirect(url_for('main.list_cities'))


def gdisconnect():
    """Provides functionality to logout of the user's Google account"""
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps("Current user is not connect."),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token={0}'.\
          format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(
            json.dumps("Failed to revoke token for given user."),
            400
        )
        response.headers['Content-Type'] = 'application/json'
        return response


def fbdisconnect():
    """Provides functionality to logout of the user's Facebook account"""
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = "https://graph.facebook.com/{0}/permissions?access_token={1}".\
           format(facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."