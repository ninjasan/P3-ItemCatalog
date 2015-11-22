__author__ = 'poojm'
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    """Summary of User Class.

    Object that contains information about registered users

    Attributes:
        id: An integer representing a unique identifier for the user
        name: A string representing the name of the user, as it was specified
                on the 3rd party, that was used to sign-in for the first time
        email: A string representing the email address for the user, from the
                3rd party site that was used to sign-in, for the first time
        picture_url: A string representing the picture for the user, from the
                3rd party site that was used to sign-in, for the first time
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    picture_url = Column(String(100))


class City(Base):
    """Summary of City Class.

    Object that contains information about a City

    Attributes:
        id: An integer representing a unique identifier for the city
        user_id: An integer representing the id of the user who create it
        name: A string representing the name of the city
        state_provence: A string representing the state or provence in which
                this city exists
        country: A string representing the country in which this city exists
        description: A string written by the user that can be used to learn
                more about a location
        image: A string representing the url of an image for the city
    """
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(60), nullable=False)
    state_provence = Column(String(100))
    country = Column(String(100))
    description = Column(String(1000))
    image = Column(String(150))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object in easily seriabilizable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
            'state_provence': self.state_provence,
            'country': self.country,
            'description': self.description,
            'image': self.image
        }


class Activity(Base):
    """Summary of Activity Class.

    Object that contains information about a City

    Attributes:
        id: An integer representing a unique identifier for the activity
        city_id: An integer representing a unique identifier for the city
                that has this activity
        user_id: An integer representing the id of the user who create it
        name: A string representing the name of the activity
        category: A string representing the category that the activity
                falls in
        description: A string written by the user that can be used to learn
                more about the activity
        website: A string representing the url of the website for an activity
        address: A string representing the street address of the activity
        image: A string representing the url of an image for the activity
    """
    __tablename__ = 'activity'
    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('city.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    category = Column(String(30))
    description = Column(String(1000))
    website = Column(String(150))
    address = Column(String(100))
    image = Column(String(150))
    city = relationship(City)
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object in easily seriabilizable format"""
        return {
            'name': self.name,
            'id': self.id,
            'city_id': self.city_id,
            'user_id': self.user_id,
            'category': self.category,
            'description': self.description,
            'website': self.website,
            'address': self.address,
            'image': self.image
        }


engine = create_engine('sqlite:///vacation_catalog_wUsers.db')
Base.metadata.create_all(engine)
