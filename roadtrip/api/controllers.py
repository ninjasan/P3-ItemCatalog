"""Contains the API controllers for the app"""
__author__ = 'poojm'

from flask import Blueprint, jsonify
from roadtrip.data.models import City, Activity
from roadtrip.data.dbsession import session
from roadtrip.main.helpers import get_city

api = Blueprint('api', __name__)


@api.route('cities/JSON/')
def cities_json():
    """Returns list of cities in JSON format."""
    cities = session.query(City).all()
    return jsonify(cities=[city.serialize for city in cities])


@api.route('cities/<int:city_id>/JSON/')
def city_json(city_id):
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


@api.route('cities/<int:city_id>/activities/JSON/')
def city_activities_json(city_id):
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


@api.route('cities/<int:city_id>/activities/<int:activity_id>/JSON/')
def activity_json(city_id, activity_id):
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
