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
This module contains collections for easy retrieval of standard lists or scalars from the database with gauged catchment
data.
"""
from math import sqrt
from operator import attrgetter
from sqlalchemy import or_, between, text
from sqlalchemy.sql.functions import func
# Current package imports
from .entities import Catchment, Descriptors, AmaxRecord
from . import loaders
from . import db


class CatchmentCollections(object):
    """
    Collections of frequently used :class:`floodestimation.entities.Catchment` objects.

    The collections objects must be passed a session to a database containing the data. This is typically
    :meth:`floodestimation.db.Session()`
    """
    def __init__(self, db_session, load_data='auto'):
        """

        :param db_session: SQLAlchemy database session
        :type db_session: :class:`sqlalchemy.orm.session.Session`
        :type load_data: `auto`: automatically load gauged catchment data from NRFA website,
                         `force`: delete all exsting data first,
                         `manual`: manually retrieve data
        :return: a catchment collection object
        :rtype: :class:`.CatchmentCollections`
        """
        self.db_session = db_session

        # If the database does not contain any catchmetnts yet, retrieve them from NRFA website and save to db
        if load_data == 'force':
            self.delete_gauged_catchments()
        if self._db_empty() and load_data in ['auto', 'force']:
            self.load_gauged_catchments()
            self.db_session.commit()

    @staticmethod
    def delete_gauged_catchments():
        """
        Delete all catchment data from the database
        """
        db.reset_db_tables()

    def load_gauged_catchments(self):
        """
        Load all catchment data into the database by downloading the data from the NRFA website
        """
        loaders.gauged_catchments_to_db(self.db_session)

    def _db_empty(self):
        return bool(self.db_session.query(Catchment).count()==0)

    def catchment_by_number(self, number):
        """
        Return a single catchment by NRFA station number

        :param number: NRFA gauging station number
        :type number: int
        :return: relevant catchment if exist or `None` otherwise
        :rtype: :class:`floodestimation.entities.Catchment`
        """
        return self.db_session.query(Catchment).get(number)

    def nearest_qmed_catchments(self, subject_catchment, limit=None, dist_limit=500):
        """
        Return a list of catchments sorted by distance to `subject_catchment` **and filtered to only include catchments
        suitable for QMED analyses**.

        :param subject_catchment: catchment object to measure distances to
        :type subject_catchment: :class:`floodestimation.entities.Catchment`
        :param limit: maximum number of catchments to return. Default: `None` (returns all available catchments).
        :type limit: int
        :param dist_limit: maximum distance in km. between subject and donor catchment. Default: 500 km. Increasing the
                           maximum distance will increase computation time!
        :type dist_limit: float or int
        :return: list of catchments sorted by distance
        :rtype: list of :class:`floodestimation.entities.Catchment`
        """

        dist_sq = Catchment.distance_to(subject_catchment).label('dist_sq')  # Distance squared, calculated using SQL
        query = self.db_session.query(Catchment, dist_sq).\
            join(Catchment.amax_records).\
            join(Catchment.descriptors).\
            filter(Catchment.id != subject_catchment.id,            # Exclude subject catchment itself
                   Catchment.is_suitable_for_qmed,                  # Only catchments suitable for QMED estimation
                   Catchment.country == subject_catchment.country,  # SQL dist method does not cover cross-boundary dist
                   # Within the distance limit
                   dist_sq <= dist_limit ** 2).\
            group_by(Catchment).\
            order_by(dist_sq).\
            having(func.count(AmaxRecord.catchment_id) >= 10)       # At least 10 AMAX records

        if limit:
            rows = query[0:limit]
        else:
            rows = query.all()

        # Add real `dist` attribute to catchment list using previously calculated SQL dist squared
        catchments = []
        for row in rows:
            catchment = row[0]
            catchment.dist = sqrt(row[1])
            catchments.append(catchment)

        return catchments

    def most_similar_catchments(self, subject_catchment, similarity_dist_function, records_limit=500,
                                include_subject_catchment='auto'):
        """
        Return a list of catchments sorted by hydrological similarity defined by `similarity_distance_function`

        :param subject_catchment: subject catchment to find similar catchments for
        :type subject_catchment: :class:`floodestimation.entities.Catchment`
        :param similarity_dist_function: a method returning a similarity distance measure with 2 arguments, both
                                         :class:`floodestimation.entities.Catchment` objects
        :param include_subject_catchment: - `auto`: include subject catchment if suitable for pooling and if urbext < 0.03
                                          - `force`: always include subject catchment
                                          - `exclude`: do not include the subject catchment
        :type include_subject_catchment: str
        :return: list of catchments sorted by similarity
        :type: list of :class:`floodestimation.entities.Catchment`
        """
        query = self.db_session.query(Catchment).join(Descriptors). \
            filter(Catchment.is_suitable_for_pooling,
                   or_(Descriptors.urbext2000 < 0.03, Descriptors.urbext2000 == None))
        if include_subject_catchment == 'exclude':
            # Remove subject catchment from donor list (if already in)
            query = query.filter(Catchment.id != subject_catchment.id)
        elif include_subject_catchment == 'force':
            # Add the subject catchment regardless of urbext of pooling suitability
            sc_query = self.db_session.query(Catchment).filter(Catchment.id == subject_catchment.id)
            query = query.union(sc_query)
        #else:
        #    catchments = query.all()
        catchments = query.all()

        # Store the similarity distance as an additional attribute for each catchment
        for catchment in catchments:
            catchment.similarity_dist = similarity_dist_function(subject_catchment, catchment)
        # Then simply sort by this attribute
        catchments.sort(key=attrgetter('similarity_dist'))

        # Limit catchments until total amax_records counts is at least `records_limit`, default 500
        amax_records_count = 0
        catchments_limited = []
        for catchment in catchments:
            catchments_limited.append(catchment)
            amax_records_count += len(catchment.amax_records)
            if amax_records_count >= records_limit:
                break

        return catchments_limited
