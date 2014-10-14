# -*- coding: utf-8 -*-

from floodestimation import db
from floodestimation.entities import Catchment, Descriptors, AmaxRecord
from floodestimation.analysis import QmedAnalysis
from floodestimation.collections import CatchmentCollections
import numpy as np
from sqlalchemy import or_
from sqlalchemy.sql.functions import func
from multiprocessing.pool import ThreadPool, Pool


db_session = db.Session()
gauged_catchments = CatchmentCollections(db_session)


def analyse_catchment(number):
    result = {}
    c = gauged_catchments.catchment_by_number(number)
    result['id'] = c.id
    analysis = QmedAnalysis(c)
    result['qmed_amax'] = analysis.qmed(method='amax_records')
    result['qmed_descr'] = analysis.qmed(method='descriptors')
    result['qmed_descr_1999'] = analysis.qmed(method='descriptors_1999')
    analysis.gauged_catchments = gauged_catchments
    result['qmed_descr_idw'] = analysis.qmed(method='descriptors')
    analysis.donor_weighting = 'equal'
    result['qmed_descr_first'] = analysis.qmed(method='descriptors', donor_catchments=analysis.find_donor_catchments(1))
    db_session.close()
    return result


if __name__ == '__main__':
    # rural_catchments = db_session.query(Catchment).join(Descriptors).join(Catchment.amax_records). \
    # filter(Catchment.is_suitable_for_qmed,
    #            Descriptors.centroid_ngr != None,
    #            or_(Descriptors.urbext2000 < 0.03, Descriptors.urbext2000 == None)). \
    #     group_by(Catchment). \
    #     having(func.count(AmaxRecord.catchment_id) > 2). \
    #     all()
    rural_catchment_ids = []
    with open(r'.\data\Science_report_stations.txt') as stations_file:
        for line in stations_file:
            rural_catchment_ids.append(int(line))
    n = len(rural_catchment_ids)
    print("Total number of rural catchments: {}".format(n))

    with open('output.txt', mode='w') as output_file:
        for i, id in enumerate(rural_catchment_ids):
            print(i, id)
            output = analyse_catchment(id)
            output_file.write(
                "{id}, {qmed_amax}, {qmed_descr}, {qmed_descr_idw}, {qmed_descr_first}, {qmed_descr_1999}\n"
                .format(**output))
