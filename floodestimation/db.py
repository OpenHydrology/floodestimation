from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import floodestimation.settings as settings



# Base class all entities that should be stored as a table in the database should be inheriting from
Base = declarative_base()

# Set up database engine and session class
engine = create_engine('sqlite:///' + settings.DB_FILE_PATH)
# When interaction with the database, modules should start a new `session` instance by simply calling `Session()`
Session = sessionmaker(engine)


def create_new_db():
    global engine
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)