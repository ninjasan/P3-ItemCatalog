__author__ = 'poojm'
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    picture_url = Column(String(100))


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(60), nullable=False)
    state_provence = Column(String(100))
    country = Column(String(100))
    description = Column(String(1000))
    image = Column(String(150))
    user = relationship(User)


class Activity(Base):
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

engine = create_engine('sqlite:///vacation_catalog_wUsers.db')
Base.metadata.create_all(engine)
