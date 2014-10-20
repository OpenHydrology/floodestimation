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


def analyse_catchment(number, gauged_catchments):
    result = {}
    catchment = gauged_catchments.catchment_by_number(number)
    result['id'] = catchment.id

    analysis = QmedAnalysis(catchment)
    result['qmed_amax'] = analysis.qmed(method='amax_records')
    result['qmed_descr'] = analysis.qmed(method='descriptors')
    result['qmed_descr_1999'] = analysis.qmed(method='descriptors_1999')

    analysis.gauged_catchments = gauged_catchments
    donors = analysis.find_donor_catchments()
    analysis.idw_power = 2
    result['qmed_descr_idw'] = analysis.qmed(method='descriptors', donor_catchments=donors)

    analysis.idw_power = 4
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

    gauged_catchments = CatchmentCollections(db_session)

    rural_catchment_ids = science_report_catchment_ids()
    print("Total number of catchments: {}".format(len(rural_catchment_ids)))

    with open('output.txt', mode='w') as output_file:
        for i, id in enumerate(rural_catchment_ids):
            print(i, id)
            output = analyse_catchment(id, gauged_catchments)
            output_file.write(
                "{id}, {qmed_amax}, {qmed_descr}, {qmed_descr_idw}, {qmed_descr_first}, {qmed_descr_1999}, {qmed_descr_idw3}\n"
                .format(**output))

    db_session.close()
