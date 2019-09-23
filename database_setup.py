# <CONFIGURATION CODE>
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
# ^imports all modules needed
Base = declarative_base()
# ^creates instance of declarative base
# (notifies SQLAlchemy that the classes from here should be mapped to tables in DB)
# </CONFIGURATION CODE>


# <CLASS CODE> (represents data in Python)
class Restaurant(Base):
    # <TABLE> (represents specific table in a DB)
    __tablename__ = 'restaurant'
    # </TABLE>
    # </MAPPER> (connects the columns of a table to a class-representative)
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    # </MAPPER>

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(Base):
    # <TABLE>
    __tablename__ = 'menu_item'
    # </TABLE>
    # <MAPPER>
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    # </MAPPER>
# </CLASS CODE>


# We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }


# <CONFIGURATION CODE>
engine = create_engine('sqlite:///restaurantmenu.db')


Base.metadata.create_all(engine)
# ^creates/connects DB and adds tables & columns
# (goes into DB and creates new tables represented by classes from here)
# </CONFIGURATION CODE>
