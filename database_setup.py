__author__ = 'poojm'
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class City(Base):
    __tablename__ = 'city'
    name = Column(String(60), nullable=False)
    state_provence = Column(String(100))
    country = Column(String(100))
    id = Column(Integer, primary_key=True)


class Activity(Base):
    __tablename__ = 'activity'
    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('city.id'))
    category = Column(String(30))
    description = Column(String(250))
    website = Column(String(150))
    image = Column(String(150))
    city = relationship(City)

engine = create_engine('sqlite:///vacation_catalog.db')
Base.metadata.create_all(engine)
