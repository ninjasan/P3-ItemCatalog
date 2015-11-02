__author__ = 'poojm'
from flask import Flask, render_template, url_for, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Activity

app = Flask(__name__)

engine = create_engine('sqlite:///vacation_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

debugging = True
#fake data for now
my_city = {'name': "Seattle", 'id': 1}
#cities = [{'name': "Seattle", 'id': 1},
#          {'name': "Portland", 'id': 2},
#          {'name': "Vancouver", "id": 3},
#          {'name': "Chicago", "id": 4}]
my_activity = {'name': "Greenlake", 'id': 1, 'city_id': 2, 'description': "walk around the lake", 'category': "outdoors"}
#activities = [{'name': "Greenlake", 'id': 1, 'city_id': 2, 'description': "walk around the lake", 'category': "outdoors"},
#              {'name': "mkt.", 'id': 2, 'city_id': 2, 'description': "eat delicious food by Ethan Stowell", 'category': "food"},
#              {'name': "Chihuly Glass Garden", 'id': 3, 'city_id': 2, 'description': "gorgeous glass museum", 'category': "museums"},
#              {'name': "Space Needle", 'id': 4, 'city_id': 2, 'description': "Visit Seattle's vision of the future from the 1969 World's Fair", 'category': "sightseeing"}]

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
        city_to_add = City(name=request.form['name'])
        session.add(city_to_add)
        session.commit()

        return redirect(url_for('list_cities'))
    else:
        return render_template('new_city.html')


@app.route('/cities/<int:city_id>/edit/', methods=['GET', 'POST'])
def edit_city(city_id):
    city = session.query(City).filter(City.id == city_id).one()
    if request.method == 'POST':
        session.query(City).filter(City.id == city_id).update({City.name: request.form['name'],
                                                               City.state_provence: request.form['state'],
                                                               City.country: request.form['country']},
                                                              synchronize_session=False)
        session.commit()
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

        return redirect(url_for('list_cities'))
    else:
        return render_template('delete_city.html', city=city)


@app.route('/cities/<int:city_id>/activities/')
@app.route('/cities/<int:city_id>/')
def show_city(city_id):
    city = session.query(City).filter(City.id == city_id).one()
    activities = session.query(Activity).filter(Activity.city_id == city_id).all()
    return render_template('show_city.html', city=city, activities=activities)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/')
def show_activity(city_id, activity_id):
    city = session.query(City).filter(City.id == city_id).one()
    activity = session.query(Activity).filter(Activity.id == activity_id).one()
    return render_template('show_activity.html', city=city, activity=activity)


@app.route('/cities/<int:city_id>/activities/new/', methods=['GET', 'POST'])
def new_activity(city_id):
    city = session.query(City).filter(City.id == city_id).one()
    if request.method == 'POST':
        activity_to_add = Activity(name=request.form['name'],
                                   city_id=city_id,
                                   category=request.form['category'],
                                   description=request.form['description'])
        session.add(activity_to_add)
        session.commit()

        return redirect(url_for('show_city', city_id=city_id))
    else:
        return render_template('new_activity.html', city=city)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/edit/', methods=['GET', 'POST'])
def edit_activity(city_id, activity_id):
    city = session.query(City).filter(City.id == city_id).one()
    activity = session.query(Activity).filter(Activity.id == activity_id).one()
    if request.method == 'POST':
        session.query(Activity).filter(Activity.id == activity_id).update({Activity.name: request.form['name'],
                                                                           Activity.description: request.form['description'],
                                                                           Activity.category: request.form['category'],
                                                                           Activity.website: request.form['website']})
        session.commit()
        return redirect(url_for('show_activity', city_id=city_id, activity_id=activity_id))
    else:
        return render_template('edit_activity.html', city=city, activity=activity)


@app.route('/cities/<int:city_id>/activities/<int:activity_id>/delete/')
def delete_activity(city_id, activity_id):
    return render_template('delete_activity.html', city=my_city, activity=my_activity)


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
