"""Contains helper functions for the application"""
__author__ = 'poojm'

import random
import string
from flask import abort, request
from flask import session as login_session
from sqlalchemy.orm.exc import NoResultFound
from roadtrip.data.models import User, City, Activity
from roadtrip.data.dbsession import session
from functools import wraps


# helper functions
def create_user(login_session):
    """
    Provides:
        Functionality to create a new user in the database

    Args:
        login_session: the dictionary storing login details
    """
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture_url=login_session['picture']
    )
    session.add(new_user)
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
    except NoResultFound:
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
        for x in xrange(32)
    )


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


def set_user_info(provider, data, data_pic):
    """
    Provides:
        Functionality to set the login_session based on the sign-in and then
        gets checks to see if this user already exists in the DB. If not, the
        user gets created. The user_id is also set as part of this function.

    Args:
        provider: which 3rd party is providing the authentication
        data: the basic information about the user
        data_pic: the picture url of the user
    """
    login_session['provider'] = provider
    if login_session['provider'] == 'google':
        login_session['username'] = data["name"]
        login_session['picture'] = data["picture"]
        login_session['email'] = data["email"]
    else:
        login_session['provider'] = 'facebook'
        login_session['username'] = data["name"]
        login_session['email'] = data["email"]
        login_session['picture'] = data_pic["data"]["url"]

    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id


def nonce_required(f):
    """
    Decorator function that checks for the presence and value of the nonce
    on any action that would change the DB (i.e. on POSTs). If the check fails,
    the a 403 page is shown, otherwise continue on like normal.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            if 'nonce' not in login_session:
                abort(403)
            elif login_session['nonce'] != request.form['nonce']:
                del login_session['nonce']
                abort(403)
            else:
                del login_session['nonce']
        return f(*args, **kwargs)
    return decorated_function
