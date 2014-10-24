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

from floodestimation import db
from floodestimation.entities import Catchment, Descriptors, AmaxRecord
from floodestimation.analysis import QmedAnalysis
from floodestimation.collections import CatchmentCollections
from sqlalchemy import or_
from sqlalchemy.sql.functions import func
from math import sqrt


class ScienceReportCollections(CatchmentCollections):
    def __init__(self, db_session, load_data='auto'):
        self.catchment_ids = science_report_catchment_ids()
        super().__init__(db_session, load_data)

    def all_catchments(self):
        query = self.db_session.query(Catchment). \
            filter(Catchment.id.in_(self.catchment_ids))
        return query.all()

    def nearest_qmed_catchments(self, subject_catchment, limit=None, dist_limit=500):
        dist_sq = Catchment.distance_to(subject_catchment).label('dist_sq')  # Distance squared, calculated using SQL
        query = self.db_session.query(Catchment, dist_sq). \
            join(Catchment.descriptors). \
            filter(Catchment.id != subject_catchment.id,  # Exclude subject catchment itself
                   Catchment.id.in_(self.catchment_ids),
                   Catchment.country == subject_catchment.country,  # SQL dist method does not cover cross-boundary dist
                   # Within the distance limit
                   dist_sq <= dist_limit ** 2). \
            group_by(Catchment). \
            order_by(dist_sq)

        if limit:
            rows = query[0:limit]  # Each row is tuple of (catchment, distance squared)
        else:
            rows = query.all()

        # Add real `dist` attribute to catchment list using previously calculated SQL dist squared
        catchments = []
        for row in rows:
            catchment = row[0]
            catchment.dist = sqrt(row[1])
            catchments.append(catchment)

        return catchments


def analyse_catchment(catchment, gauged_catchments):
    result = {}
    result['id'] = catchment.id

    analysis = QmedAnalysis(catchment)
    result['qmed_amax'] = analysis.qmed(method='amax_records')
    result['qmed_descr'] = analysis.qmed(method='descriptors')
    result['qmed_descr_1999'] = analysis.qmed(method='descriptors_1999')

    analysis.gauged_catchments = gauged_catchments
    donors = analysis.find_donor_catchments()
    analysis.idw_power = 2
    result['qmed_descr_idw'] = analysis.qmed(method='descriptors', donor_catchments=donors)

    analysis.idw_power = 3
    result['qmed_descr_idw3'] = analysis.qmed(method='descriptors', donor_catchments=donors)

    analysis.donor_weighting = 'equal'
    result['qmed_descr_first'] = analysis.qmed(method='descriptors', donor_catchments=donors[0:1])

    return result


def science_report_catchment_ids():
    result = []
    with open(r'.\data\Science_report_stations.txt') as stations_file:
        for line in stations_file:
            result.append(int(line))
    return result


def nrfa_qmed_catchments(db_session):
    return db_session.query(Catchment).join(Descriptors).join(Catchment.amax_records). \
        filter(Catchment.is_suitable_for_qmed,
               Descriptors.centroid_ngr != None,
               or_(Descriptors.urbext2000 < 0.03, Descriptors.urbext2000 == None)). \
        group_by(Catchment). \
        having(func.count(AmaxRecord.catchment_id) >= 10). \
        all()


if __name__ == '__main__':
    db_session = db.Session()

    science_report_collections = ScienceReportCollections(db_session)
    feh_catchments_collections = CatchmentCollections(db_session)

    subject_catchments = science_report_collections.all_catchments()
    print("Total number of catchments: {}".format(len(subject_catchments)))

    with open('output.txt', mode='w') as output_file:
        for i, catchment in enumerate(subject_catchments):
            print(i, catchment.id)
            #output = analyse_catchment(catchment, feh_catchments_collections)
            output = analyse_catchment(catchment, science_report_collections)
            output_file.write(
                "{id}, {qmed_amax}, {qmed_descr}, {qmed_descr_idw}, {qmed_descr_first}, {qmed_descr_1999}, {qmed_descr_idw3}\n"
                .format(**output))

    db_session.close()
