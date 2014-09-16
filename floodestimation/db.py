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

Interaction with the database is typically as follows::

    from floodestimation import db

    # Once:
    session = db.Session()

    # As and when required:
    session.add(...)    # Load data
    session.query(...)  # Retrieve data
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