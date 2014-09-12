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

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
# Current package imports
from . import settings

# Base class all entities that should be stored as a table in the database should be inheriting from
Base = declarative_base()

# Set up database engine and session class
engine = create_engine('sqlite:///' + settings.DB_FILE_PATH)
metadata = MetaData(bind=engine, reflect=True)

# When interaction with the database, modules should start a new `session` instance by simply calling `Session()`.
Session = sessionmaker(bind=engine)