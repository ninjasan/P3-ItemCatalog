__author__ = 'poojm'
from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Activity

engine = create_engine('sqlite:///vacation_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


@app.route('/')
@app.route('/home/')
@app.route('/index/')
@app.route('/cities/')
def list_cities():
    return "All the cities!"


@app.route('/cities/<int:city_id>/')
def city(city_id):
    return "Just one city"


@app.route('/cities/new/')
def new_city():
    return "Let's create a new city!"


@app.route('/cities/<int:city_id>/edit/')
def edit_city(city_id):
    return "We need to fix this city!"


@app.route('/cities/<int:city_id>/delete/')
def delete_city(city_id):
    return "We don't really need that city... do we?"


@app.route('/cities/<int:city_id>/activities/')
def list_activities(city_id):
    return "List all the activities!"


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/')
def activity(city_id, activity_id):
    return "Just this one activity!"


@app.route('/cities/<int:city_id>/activities/new/')
def new_activity(city_id):
    return "This place needs more things to do!"


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/edit/')
def edit_activity(city_id, activity_id):
    return "Let's change this thing!"


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/delete/')
def delete_activity(city_id, activity_id):
    return "This activity no longer exists."


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
