"""Contains the API controllers for the app"""
__author__ = 'poojm'

from flask import Blueprint, jsonify, Response
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from roadtrip.data.models import City, Activity
from roadtrip.data.dbsession import session
from roadtrip.main.helpers import get_city, get_activity

api = Blueprint('api', __name__)


@api.route('cities/JSON/')
def cities_json():
    """Returns list of cities in JSON format."""
    cities = session.query(City).all()
    return jsonify(cities=[city.serialize for city in cities])


@api.route('cities/XML/')
def cities_xml():
    """Returns list of cities in XML format."""
    cities = session.query(City).all()
    cities_in_xml = dicttoxml(city.serialize for city in cities)
    cities_in_pretty_xml = parseString(cities_in_xml).toprettyxml()
    return Response(cities_in_pretty_xml, mimetype='text/xml')


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


@api.route('cities/<int:city_id>/XML/')
def city_xml(city_id):
    """
    Provides:
        Functionality to get a city and transform it into XML

    Args:
        city_id: the unique identifier for the city

    Returns:
        XML formatted city information
    """
    city = get_city(city_id)
    city_in_xml = dicttoxml(city.serialize)
    city_in_pretty_xml = parseString(city_in_xml).toprettyxml()
    return Response(city_in_pretty_xml, mimetype='text/xml')


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


@api.route('cities/<int:city_id>/activities/XML/')
def city_activities_xml(city_id):
    """
    Provides:
        Functionality to get a activities for a city and transform it into XML

    Args:
        city_id: the unique identifier for the city.

    Returns:
        XML formatted list of activities for a city
    """
    activities = \
        session.query(Activity).filter(Activity.city_id == city_id).all()
    activities_in_xml = dicttoxml(activity.serialize for activity in activities)
    activities_in_pretty_xml = parseString(activities_in_xml).toprettyxml()
    return Response(activities_in_pretty_xml, mimetype='text/xml')


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
    activity = get_activity(city_id, activity_id)
    return jsonify(activity=activity.serialize)


@api.route('cities/<int:city_id>/activities/<int:activity_id>/XML/')
def activity_xml(city_id, activity_id):
    """
    Provides:
        Functionality to get an activity and transform it into XML

    Args:
        city_id: the unique identifier for the city.
        activity_id: the unique identifier for the activity in that city

    Returns:
        XML formatted activity information
    """
    activity = get_activity(city_id, activity_id)
    activity_in_xml = dicttoxml(activity.serialize)
    activity_in_pretty_xml = parseString(activity_in_xml).toprettyxml()
    return Response(activity_in_pretty_xml, mimetype='text/xml')
