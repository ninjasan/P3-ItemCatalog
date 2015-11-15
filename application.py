__author__ = 'poojm'
from flask import Flask, render_template, url_for, request, redirect, flash
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, City, Activity
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random, string
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Roadtrip Catalog App"

app = Flask(__name__)

engine = create_engine('sqlite:///vacation_catalog_wUsers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

debugging = True

@app.route('/login/')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/')
@app.route('/home/')
@app.route('/index/')
@app.route('/cities/')
def list_cities():
    cities = session.query(City).all()
    # adding print for debugging purposes
    if debugging:
        for city in cities:
            print city.name
            activities = session.query(Activity).filter(Activity.city_id == city.id).all()
            for activity in activities:
                print "    " + activity.name
    return render_template('list_cities.html', cities=cities)


@app.route('/cities/new/', methods=['GET', 'POST'])
def new_city():
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
        return render_template('new_city.html')


@app.route('/cities/<int:city_id>/edit/', methods=['GET', 'POST'])
def edit_city(city_id):
    city = session.query(City).filter(City.id == city_id).one()
    if request.method == 'POST':
        session.query(City).filter(City.id == city_id).update({City.name: request.form['name'],
                                                               City.state_provence: request.form['state'],
                                                               City.country: request.form['country'],
                                                               City.description: request.form['description'],
                                                               City.image: request.form['image']},
                                                              synchronize_session=False)
        session.commit()
        flash("{0} has been successfully editted".format(city.name))
        return redirect(url_for('show_city', city_id=city.id))
    else:
        if 'user_id' not in login_session or city.user_id != login_session['user_id']:
            return redirect(url_for('show_city', city_id=city.id))
        else:
            return render_template('edit_city.html', city=city)


@app.route('/cities/<int:city_id>/delete/', methods=['GET', 'POST'])
def delete_city(city_id):
    city = session.query(City).filter(City.id == city_id).one()
    activities = session.query(Activity).filter(Activity.city_id == city_id).all()
    if request.method == 'POST':
        session.delete(city)
        for activity in activities:
            session.delete(activity)
        session.commit()
        flash("The location has been successfully delete.")
        return redirect(url_for('list_cities'))
    else:
        if 'user_id' not in login_session or city.user_id != login_session['user_id']:
            return redirect(url_for('show_city', city_id=city.id))
        else:
            return render_template('delete_city.html', city=city)


@app.route('/cities/<int:city_id>/activities/')
@app.route('/cities/<int:city_id>/')
def show_city(city_id):
    city = session.query(City).filter(City.id == city_id).one()
    activities = session.query(Activity).filter(Activity.city_id == city_id).all()
    creator = session.query(User).filter(User.id == City.user_id).one()

    if 'user_id' not in login_session or creator.id != login_session['user_id']:
        return render_template('show_city_public.html', city=city, activities=activities, creator=creator)
    else:
        return render_template('show_city.html', city=city, activities=activities, creator=creator)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/')
def show_activity(city_id, activity_id):
    city = session.query(City).filter(City.id == city_id).one()
    activity = session.query(Activity).filter(Activity.id == activity_id).one()
    creator = session.query(User).filter(User.id == activity.user_id).one()
    if 'user_id' not in login_session or creator.id != login_session['user_id']:
        return render_template('show_activity_public.html', city=city, activity=activity, creator=creator)
    else:
        return render_template('show_activity.html', city=city, activity=activity, creator=creator)


@app.route('/cities/<int:city_id>/activities/new/', methods=['GET', 'POST'])
def new_activity(city_id):
    city = session.query(City).filter(City.id == city_id).one()
    if request.method == 'POST':
        print "in activity post"
        print request.form
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
        flash("{0} has been successfully added to {1}".format(activity_to_add.name, city.name))
        return redirect(url_for('show_city', city_id=city_id))
    else:
        return render_template('new_activity.html', city=city)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/edit/', methods=['GET', 'POST'])
def edit_activity(city_id, activity_id):
    city = session.query(City).filter(City.id == city_id).one()
    activity = session.query(Activity).filter(Activity.id == activity_id).one()
    if request.method == 'POST':
        session.query(Activity).filter(Activity.id == activity_id).update({Activity.name: request.form['name'],
                                                                           Activity.address: request.form['address'],
                                                                           Activity.description: request.form['description'],
                                                                           Activity.category: request.form['category'],
                                                                           Activity.website: request.form['website'],
                                                                           Activity.image: request.form['image']})
        session.commit()
        flash("This item has been successfully editted!")
        return redirect(url_for('show_activity', city_id=city_id, activity_id=activity_id))
    else:
        if 'user_id' not in login_session or activity.user_id != login_session['user_id']:
            return redirect(url_for('show_activity', city_id=city_id, activity_id=activity_id))
        else:
            return render_template('edit_activity.html', city=city, activity=activity)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/delete/', methods=['GET', 'POST'])
def delete_activity(city_id, activity_id):
    city = session.query(City).filter(City.id == city_id).one()
    activity = session.query(Activity).filter(Activity.id == activity_id).one()
    if request.method == 'POST':
        session.delete(activity)
        session.commit()
        flash("The activity has been successfully deleted from {0}".format(city.name))
        return redirect(url_for('show_city', city_id=city_id))
    else:
        if 'user_id' not in login_session or activity.user_id != login_session['user_id']:
            return redirect(url_for('show_activity', city_id=city_id, activity_id=activity_id))
        else:
            return render_template('delete_activity.html', city=city, activity=activity)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print "here!"
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Connect-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data

    try:
        # turn the auth code into a credentials object
        print "trying to turn auth code into creds object"
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
    print "checking that access token is valid"
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there was an error int he access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    print "verifying that the access token is for the right user"
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user Id doesn't match the given user ID."), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that that access token is valid for this app.
    print "verifying that access token is for the right app"
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's"), 401)
        print "Token's client ID doesn't match app's"
        response.headers['Content-Type'] = 'application/json'
        return response

    print "storing creds"
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store access token in the session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # get user info (to prove you can)
    print "getting user info"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # see if user exists
    user_id = getUserId(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    print "Username: " + login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    print "picture url: " + login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    print output
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user is not connect."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token={0}'.format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps("Failed to revoke token for given user."), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received {0}".format(access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
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

    url = "https://graph.facebook.com/v2.4/me?{0}&fields=name,id,email".format(token)
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
    url = "https://graph.facebook.com/v2.4/me/picture?{0}&redirect=0&height=200&width=200".format(token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = "https://graph.facebook.com/{0}/permissions?access_token={1}".format(facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect/')
def disconnect():
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
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture_url=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter(User.email == login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter(User.id == user_id).one()
    return user

def getUserId(email):
    try:
        user = session.query(User).filter(User.email == email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
