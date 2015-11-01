__author__ = 'poojm'
from flask import Flask, render_template, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Activity

app = Flask(__name__)

engine = create_engine('sqlite:///vacation_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#fake data for now
my_city = {'name': "Seattle", 'id': 1}
cities = [{'name': "Seattle", 'id': 1},
          {'name': "Portland", 'id': 2},
          {'name': "Vancouver", "id": 3},
          {'name': "Chicago", "id": 4}]
my_activity = {'name': "Greenlake", 'id': 1, 'city_id': 1, 'description': "walk around the lake", 'category': "outdoors"}
activities = [{'name': "Greenlake", 'id': 1, 'city_id': 1, 'description': "walk around the lake", 'category': "outdoors"},
              {'name': "mkt.", 'id': 2, 'city_id': 1, 'description': "eat delicious food by Ethan Stowell", 'category': "food"},
              {'name': "Chihuly Glass Garden", 'id': 3, 'city_id': 1, 'description': "gorgeous glass museum", 'category': "museums"},
              {'name': "Space Needle", 'id': 4, 'city_id': 1, 'description': "Visit Seattle's vision of the future from the 1969 World's Fair", 'category': "sightseeing"}]

@app.route('/')
@app.route('/home/')
@app.route('/index/')
@app.route('/cities/')
def list_cities():
    return render_template('list_cities.html', cities=cities)


@app.route('/cities/<int:city_id>/')
def city(city_id):
    return "Just one city"


@app.route('/cities/new/')
def new_city():
    return "Let's create a new city!"


@app.route('/cities/<int:city_id>/edit/')
def edit_city(city_id):
    return render_template('edit_city.html', city=my_city)


@app.route('/cities/<int:city_id>/delete/')
def delete_city(city_id):
    return render_template('delete_city.html', city=my_city)


@app.route('/cities/<int:city_id>/activities/')
def list_activities(city_id):
    return render_template('list_activities.html', city=my_city, activities=activities)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/')
def activity(city_id, activity_id):
    return "Just this one activity!"


@app.route('/cities/<int:city_id>/activities/new/')
def new_activity(city_id):
    return "This place needs more things to do!"


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/edit/')
def edit_activity(city_id, activity_id):
    return render_template('edit_activity.html', city=my_city, activity=my_activity)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/delete/')
def delete_activity(city_id, activity_id):
    return render_template('delete_activity.html', city=my_city, activity=my_activity)


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
