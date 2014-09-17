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
This module contains collections for easy retrieval of standard lists or scalars from the database with gauged catchment
data.
"""

from operator import attrgetter
# Current package imports
from .entities import Catchment


class CatchmentCollections(object):
    """
    Collections of frequently used :class:`floodestimation.entities.Catchment` objects.

    The collections objects must be passed a session to a database containing the data. This is typically
    :meth:`floodestimation.db.Session()`
    """
    def __init__(self, db_session):
        """

        :param db_session: SQLAlchemy database session
        :type db_session: :class:`sqlalchemy.orm.session.Session`
        :return: a catchment collection object
        :rtype: :class:`.CatchmentCollections`
        """
        self.db_session = db_session

    def catchment_by_number(self, number):
        """
        Return a single catchment by NRFA station number

        :param number: NRFA gauging station number
        :type number: int
        :return: relevant catchment if exist or `None` otherwise
        :rtype: :class:`floodestimation.entities.Catchment`
        """
        return self.db_session.query(Catchment).get(number)

    def nearest_qmed_catchments(self, subject_catchment):
        """
        Return a list of catchment sorted by distance to `subject_catchment` **and filtered to only include catchments
        suitable for QMED analyses**.

        :param subject_catchment: catchment object to measure distances to
        :type subject_catchment: :class:`floodestimation.entities.Catchment`
        :return: list of catchments sorted by distance
        :rtype: list
        """
        # Get a list of all catchment, excluding the subject_catchment itself
        catchments = self.db_session.query(Catchment).filter(Catchment.id != subject_catchment.id,
                                                             Catchment.is_suitable_for_qmed).all()
        # Sort by distance to subject_catchment
        catchments.sort(key=lambda c: c.distance_to(subject_catchment))
        return catchments

    def most_similar_catchments(self, subject_catchment):
        raise NotImplementedError