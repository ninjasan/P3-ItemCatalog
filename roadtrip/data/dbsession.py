"""Contains database session to be used for the whole application """
__author__ = 'poojm'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from roadtrip.data.models import Base

engine = create_engine('sqlite:///vacation_catalog_wUsers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
