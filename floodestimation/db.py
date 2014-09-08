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

import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import floodestimation.settings as settings
logger = logging.getLogger(__name__)

# Base class all entities that should be stored as a table in the database should be inheriting from
Base = declarative_base()

# Set up database engine and session class
engine = create_engine('sqlite:///' + settings.DB_FILE_PATH)

# If the database does not exist, create it
if not os.path.isfile(settings.DB_FILE_PATH):
    logger.warning("Database does not exist yet. Creating at {}".format(settings.DB_FILE_PATH))
    Base.metadata.drop_all(engine)
    # We need to import all entities at this point to be able to create all tables
    import floodestimation.entities
    # Create all tables
    Base.metadata.create_all(engine)

# When interaction with the database, modules should start a new `session` instance by simply calling `Session()`.
# This statement must be AFTER the `Base.metadata.create_all` statement to make sure that whenever a module creates a
# session, a valid database exists.
Session = sessionmaker(engine)