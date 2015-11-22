__author__ = 'poojm'

from flask import Blueprint
from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify, abort
from flask import session as login_session
from roadtrip.data.models import Base, User, City, Activity
from roadtrip.data.dbsession import session
from roadtrip.main.helpers import get_city, get_activity, get_creator
from roadtrip.main.helpers import generate_key


main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
@main.route('home/')
@main.route('index/')
@main.route('login/')
def login():
    """Gives this session a unique key and renders the login page."""
    state = generate_key()
    login_session['state'] = state
    return render_template('login.html', state=state)


@main.route('about/')
def about():
    """Renders the about page."""
    return render_template('about.html')


@main.route('cities/')
def list_cities():
    """Renders the main cities page, with all the cities"""
    cities = session.query(City).all()
    if 'user_id' not in login_session:
        return render_template('list_cities_public.html', cities=cities)
    else:
        return render_template('list_cities.html', cities=cities)


@main.route('cities/new/', methods=['GET', 'POST'])
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
        return redirect(url_for('.list_cities'))
    else:
        if 'user_id' not in login_session:
            return redirect(url_for('.list_cities'))
        else:
            return render_template('new_city.html')


@main.route('cities/<int:city_id>/edit/', methods=['GET', 'POST'])
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
        return redirect(url_for('.show_city', city_id=city.id))
    else:
        if 'user_id' not in login_session or \
           city.user_id != login_session['user_id']:
            return redirect(url_for('.show_city', city_id=city.id))
        else:
            return render_template('edit_city.html', city=city)


@main.route('cities/<int:city_id>/delete/', methods=['GET', 'POST'])
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
            flash("The location has been successfully deleted.")
            del login_session['nonce']
        return redirect(url_for('.list_cities'))
    else:
        if 'user_id' not in login_session or \
           city.user_id != login_session['user_id']:
            return redirect(url_for('.show_city', city_id=city.id))
        else:
            return render_template('delete_city.html', city=city)


@main.route('cities/<int:city_id>/activities/')
@main.route('cities/<int:city_id>/')
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
    creator = get_creator(city.user_id)

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


@main.route('cities/<int:city_id>/activities/<int:activity_id>/')
def show_activity(city_id, activity_id):
    """
    Provides functionality for displaying an activity for a city

    Args:
      city_id: the unique identifier for the city.
      activity_id: the unique identifier for the activity in that city
    """
    city = get_city(city_id)
    activity = get_activity(city_id, activity_id)
    creator = get_creator(activity.user_id)

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


@main.route('cities/<int:city_id>/activities/new/', methods=['GET', 'POST'])
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
        return redirect(url_for('.show_city', city_id=city_id))
    else:
        if 'user_id' not in login_session:
            return redirect(url_for('.show_city', city_id=city_id))
        return render_template('new_activity.html', city=city)


@main.route('cities/<int:city_id>/activities/<int:activity_id>/edit/',
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
        return redirect(url_for('.show_activity',
                                city_id=city_id,
                                activity_id=activity_id))
    else:
        if 'user_id' not in login_session or \
           activity.user_id != login_session['user_id']:
            return redirect(url_for('.show_activity',
                                    city_id=city_id,
                                    activity_id=activity_id))
        else:
            return render_template('edit_activity.html',
                                   city=city,
                                   activity=activity)


@main.route('cities/<int:city_id>/activities/<int:activity_id>/delete/',
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
        return redirect(url_for('.show_city', city_id=city_id))
    else:
        if 'user_id' not in login_session or \
           activity.user_id != login_session['user_id']:
            return redirect(url_for('.show_activity',
                                    city_id=city_id,
                                    activity_id=activity_id))
        else:
            return render_template('delete_activity.html',
                                   city=city,
                                   activity=activity)
