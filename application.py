__author__ = 'poojm'
import json
import random
import string

import httplib2
import requests

from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify, make_response, abort
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, City, Activity
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

CLIENT_ID = json.loads(open('client_secret.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Roadtrip Catalog App"

app = Flask(__name__)

engine = create_engine('sqlite:///vacation_catalog_wUsers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/cities/JSON/')
def cities_JSON():
    """Returns list of cities in JSON format."""
    cities = session.query(City).all()
    return jsonify(cities=[city.serialize for city in cities])


@app.route('/cities/<int:city_id>/JSON/')
def city_JSON(city_id):
    """
    Provides:
        Functionality to get a city and transform it into JSON

    Args:
        city_id: the unique identifier for the city

    Returns:
        JSON formatted city information
    """
    city = get_city(city_id)
    return jsonify(city=city.serialize)


@app.route('/cities/<int:city_id>/activities/JSON/')
def city_activities_JSON(city_id):
    """
    Provides:
        Functionality to get a activities for a city and transform it into JSON

    Args:
        city_id: the unique identifier for the city.

    Returns:
        JSON formatted list of activities for a city
    """
    activities = \
        session.query(Activity).filter(Activity.city_id == city_id).all()
    return jsonify(activities=[i.serialize for i in activities])


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/JSON/')
def activity_JSON(city_id, activity_id):
    """
    Provides:
        Functionality to get an activity and transform it into JSON

    Args:
        city_id: the unique identifier for the city.
        activity_id: the unique identifier for the activity in that city

    Returns:
        JSON formatted activity information
    """
    activity = \
        session.query(Activity).filter(Activity.id == activity_id,
                                       Activity.city_id == city_id).one()
    return jsonify(activity=activity.serialize)


@app.errorhandler(403)
def action_unauthorized(error):
    """Redirect the user to a site built 403 page"""
    return render_template('error_403.html', error=error), 403


@app.errorhandler(404)
def entity_not_found(error):
    """Redirect the user to a site built 404 page"""
    return render_template('error_404.html', error=error), 404


@app.route('/')
@app.route('/home/')
@app.route('/index/')
@app.route('/login/')
def login():
    """Gives this session a unique key and renders the login page."""
    state = generate_key()
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/about/')
def about():
    """Renders the about page."""
    return render_template('about.html')


@app.route('/cities/')
def list_cities():
    """Renders the main cities page, with all the cities"""
    cities = session.query(City).all()
    if 'user_id' not in login_session:
        return render_template('list_cities_public.html', cities=cities)
    else:
        return render_template('list_cities.html', cities=cities)


@app.route('/cities/new/', methods=['GET', 'POST'])
def new_city():
    """
    Provides:
        Functionality for adding a new city
        On GET: render the create city page
        On POST: create a new city and adds it to the DB
    """
    if request.method == 'POST':
        city_to_add = City(name=request.form['name'],
                           state_provence=request.form['state'],
                           country=request.form['country'],
                           description=request.form['description'],
                           image=request.form['image'],
                           user_id=login_session['user_id'])
        session.add(city_to_add)
        session.commit()
        flash("{0} has been successfully added.".format(city_to_add.name))
        return redirect(url_for('list_cities'))
    else:
        if 'user_id' not in login_session:
            return redirect(url_for('list_cities'))
        else:
            return render_template('new_city.html')


@app.route('/cities/<int:city_id>/edit/', methods=['GET', 'POST'])
def edit_city(city_id):
    """
    Provides:
        Functionality for editing a city
        On GET: render the edit city page
        On POST: updates the city in the DB

    Args:
        city_id: the unique identifier for the city.
    """
    city = get_city(city_id)
    if request.method == 'POST':
        session.query(City).filter(City.id == city_id).update(
            {City.name: request.form['name'],
             City.state_provence: request.form['state'],
             City.country: request.form['country'],
             City.description: request.form['description'],
             City.image: request.form['image']},
            synchronize_session=False)
        session.commit()
        flash("{0} has been successfully edited".format(city.name))
        return redirect(url_for('show_city', city_id=city.id))
    else:
        if 'user_id' not in login_session or \
           city.user_id != login_session['user_id']:
            return redirect(url_for('show_city', city_id=city.id))
        else:
            return render_template('edit_city.html', city=city)


@app.route('/cities/<int:city_id>/delete/', methods=['GET', 'POST'])
def delete_city(city_id):
    """
    Provides functionality for deleting a city and associated activities

        On GET: render the delete city page
        On POST: deletes the city and related activities from the DB

    Args:
      city_id: the unique identifier for the city.
    """
    city = get_city(city_id)
    activities = session.query(Activity).filter(
                    Activity.city_id == city_id).all()
    if request.method == 'POST':
        if 'nonce' not in login_session or \
           login_session['nonce'] != request.form['nonce']:
            abort(403)
        else:
            session.delete(city)
            for activity in activities:
                session.delete(activity)
            session.commit()
            flash("The location has been successfully delete.")
            del login_session['nonce']
        return redirect(url_for('list_cities'))
    else:
        if 'user_id' not in login_session or \
           city.user_id != login_session['user_id']:
            return redirect(url_for('show_city', city_id=city.id))
        else:
            return render_template('delete_city.html', city=city)


@app.route('/cities/<int:city_id>/activities/')
@app.route('/cities/<int:city_id>/')
def show_city(city_id):
    """
    Provides:
        Functionality for displaying a city and associated activities

    Args:
        city_id: the unique identifier for the city.
    """
    city = get_city(city_id)
    activities = session.query(Activity).filter(
            Activity.city_id == city_id).all()
    creator = get_creator(city)

    if 'user_id' not in login_session or \
       creator.id != login_session['user_id']:
        return render_template('show_city_public.html',
                               city=city,
                               activities=activities,
                               creator=creator)
    else:
        return render_template('show_city.html',
                               city=city,
                               activities=activities,
                               creator=creator)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/')
def show_activity(city_id, activity_id):
    """
    Provides functionality for displaying an activity for a city

    Args:
      city_id: the unique identifier for the city.
      activity_id: the unique identifier for the activity in that city
    """
    city = get_city(city_id)
    activity = get_activity(city_id, activity_id)
    creator = get_creator(activity)

    if 'user_id' not in login_session or \
       creator.id != login_session['user_id']:
        return render_template('show_activity_public.html',
                               city=city,
                               activity=activity,
                               creator=creator)
    else:
        return render_template('show_activity.html',
                               city=city,
                               activity=activity,
                               creator=creator)


@app.route('/cities/<int:city_id>/activities/new/', methods=['GET', 'POST'])
def new_activity(city_id):
    """
    Provides:
        Functionality for adding a new activity for a city
        On GET: renders the form to add a new activity
        On POST: takes the input from the form and adds a new activity
                 to the DB

    Args:
        city_id: the unique identifier for the city.
    """
    city = get_city(city_id)

    if request.method == 'POST':
        activity_to_add = Activity(name=request.form['name'],
                                   city_id=city_id,
                                   address=request.form['address'],
                                   category=request.form['category'],
                                   description=request.form['description'],
                                   website=request.form['website'],
                                   image=request.form['image'],
                                   user_id=login_session['user_id'])
        session.add(activity_to_add)
        session.commit()
        flash("{0} has been successfully added to {1}".format(
                                                        activity_to_add.name,
                                                        city.name))
        return redirect(url_for('show_city', city_id=city_id))
    else:
        if 'user_id' not in login_session:
            return redirect(url_for('show_city', city_id=city_id))
        return render_template('new_activity.html', city=city)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/edit/',
           methods=['GET', 'POST'])
def edit_activity(city_id, activity_id):
    """
    Provides functionality for editing an activity for a city

        On GET: renders the form to edit an activity
        On POST: takes the input from the form and updates the activity
                 in the DB

    Args:
      city_id: the unique identifier for the city.
      activity_id: the unique identifier for the activity in that city
    """
    city = get_city(city_id)
    activity = get_activity(city_id, activity_id)

    if request.method == 'POST':
        session.query(Activity).filter(Activity.id == activity_id,
                                       Activity.city_id == city_id).update(
            {Activity.name: request.form['name'],
             Activity.address: request.form['address'],
             Activity.description: request.form['description'],
             Activity.category: request.form['category'],
             Activity.website: request.form['website'],
             Activity.image: request.form['image']})
        session.commit()
        flash("This item has been successfully edited!")
        return redirect(url_for('show_activity',
                                city_id=city_id,
                                activity_id=activity_id))
    else:
        if 'user_id' not in login_session or \
           activity.user_id != login_session['user_id']:
            return redirect(url_for('show_activity',
                                    city_id=city_id,
                                    activity_id=activity_id))
        else:
            return render_template('edit_activity.html',
                                   city=city,
                                   activity=activity)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/delete/',
           methods=['GET', 'POST'])
def delete_activity(city_id, activity_id):
    """
    Provides:
        Functionality to delete an activity in a city
        On GET: renders the form to delete an activity
        On POST: takes the input from the form and deletes the activity
                 from the DB

    Args:
        city_id: the unique identifier for the city.
        activity_id: the unique identifier for the activity in that city
    """
    city = get_city(city_id)
    activity = get_activity(city_id, activity_id)

    if request.method == 'POST':
        if 'nonce' not in login_session or \
           login_session['nonce'] != request.form['nonce']:
            abort(403)
        else:
            session.delete(activity)
            session.commit()
            flash("The activity has been successfully deleted from {0}".
                  format(city.name))
            del login_session['nonce']
        return redirect(url_for('show_city', city_id=city_id))
    else:
        if 'user_id' not in login_session or \
           activity.user_id != login_session['user_id']:
            return redirect(url_for('show_activity',
                                    city_id=city_id,
                                    activity_id=activity_id))
        else:
            return render_template('delete_activity.html',
                                   city=city,
                                   activity=activity)


@app.route('/gconnect', methods=['POST'])
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
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
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
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;' \
              'border-radius: 150px;-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
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


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Provides functionality to login the user via their Facebook account"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json',
                             'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json',
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
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Provides functionality to logout of the user's Facebook account"""
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = "https://graph.facebook.com/{0}/permissions?access_token={1}".\
           format(facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect/')
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
        return redirect(url_for('list_cities'))
    else:
        return redirect(url_for('list_cities'))


# helper functions
def create_user(login_session):
    """
    Provides:
        Functionality to create a new user in the database

    Args:
        login_session: the dictionary storing login details
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture_url=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter(
        User.email == login_session['email']
    ).one()
    return user.id

def get_user_info(user_id):
    """
    Provides:
        Functionality retrieve the user's details from the database

    Args:
        user_id: the unique identifier for the user

    Returns:
        user: an object containing the user's information
    """
    user = session.query(User).filter(User.id == user_id).one()
    return user

def get_user_id(email):
    """
    Provides:
        Functionality to see if a user has already been registered

    Args:
        email: the email address of the user, from their Facebook
            or Google account

    Returns:
        user.id or none: the unique identifier for the user,
            if the user has registered
    """
    try:
        user = session.query(User).filter(User.email == email).one()
        return user.id
    except:
        return None


def get_city(city_id):
    """
    Provides:
        functionality to get the city from the DB, if it exists
        If the city doesn't exist, we abort with a 404

    Args:
        city_id: the identifier for the city we're trying to find

    Returns:
        an object representing the city
    """
    try:
        city = session.query(City).filter(City.id == city_id).one()
    except NoResultFound, error:
        abort(404, error)
    return city


def get_activity(city_id, activity_id):
    """
    Provides:
        Functionality to get the activity from the DB, if it exists
        If the activity doesn't exist, we abort with a 404

    Args:
        city_id: the identifier for the city in which the activity exists
        activity_id: the identifier for the activity we're trying to find

    Returns:
        an object representing the activity
    """
    try:
        activity = session.query(Activity).filter(
            Activity.id == activity_id,
            Activity.city_id == city_id).one()
    except NoResultFound, error:
        abort(404, error)
    return activity


def get_creator(creator_id):
    """
    Provides:
        Functionality to get the creator from the DB, if he/she exists
        If the creator doesn't exist, we abort with a 404

    Args:
        creator_id: the identifier for the user who created the item

    Returns:
        an object representing the creator of the item
    """
    try:
        creator = session.query(User).filter(User.id == creator_id).one()
    except NoResultFound, error:
        abort(404, error)
    return creator


def generate_key():
    """
    Provides:
        Functionality to create a random code

    Returns:
        a random string of characters
    """
    return ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32))


def generate_nonce():
    """
    Provides:
        Functionality to create a random one-time use key

    Returns:
        a random one-time use key
    """
    if 'nonce' not in login_session:
        login_session['nonce'] = generate_key()
    return login_session['nonce']
app.jinja_env.globals['nonce'] = generate_nonce


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
