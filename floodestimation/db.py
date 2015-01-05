# -*- coding: utf-8 -*-

# Copyright (c) 2014  Florenz A.P. Hollebrandse <f.a.p.hollebrandse@protonmail.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides a connection with an sqlite database to store (gauged) catchment data including annual maximum flow
data and catchment descriptors.

The database connection usses the `sqlalchemy` package (`docs <sqlalchemy.org>`_) for interaction with a sqlite
database. The module contains a :class:`Base` class that all entities in :mod:`floodestimation.entities` are based on.
This enables straightforward retrieving and saving of data in relevant tables.

The sqlite database is saved in the user's application data folder. On Windows, this is folder is located
at `C:\\\\Users\\\\{Username}\\\\AppData\\\\Local\\\\Open Hydrology\\\\fehdata\\\\fehdata.sqlite`.

The database is automatically created (if it does not exist yet) when importing the :mod:`floodestimation` package.

Interaction with the database is typically as follows::

    from floodestimation import db
    from floodestimation.entities import Catchment

    # Once:
    session = db.Session()

    # As and when required:
    session.add(Catchment(...))                           # Load data
    catchments = session.query(Catchment).filter_by(...)  # Retrieve data
    session.commit()

Typically a single session instance can be used throughout a program with commits (or rollbacks) as and when required.

"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
# Current package imports
from . import settings

#: Base class all entities that should be stored as a table in the database should be inheriting from. For example:
#:
#: .. code-block:: python
#:
#:     from floodestimation import db
#:
#:     class SomeEntity(db.Base):
#:         __tablename__ = 'some_entity'
#:         ...
#:
Base = declarative_base()

# Set up database engine and session class
engine = create_engine('sqlite:///' + settings.DB_FILE_PATH)
metadata = MetaData(bind=engine, reflect=True)

# When interaction with the database, modules should start a new `session` instance by simply calling `Session()`.
Session = sessionmaker(bind=engine)


def create_db_tables():
    # Create database tables if they don't exist yet. All entities must be imported first.
    # This method is called from `floodestimation.__init__.py` to ensure that the database exist with valid tables when
    # importing and calling `Session()`.
    Base.metadata.create_all(engine)


def reset_db_tables():
    Base.metadata.drop_all(engine)
    create_db_tables()


def empty_db_tables():
    for table in reversed(metadata.sorted_tables):
        engine.execute(table.delete())
