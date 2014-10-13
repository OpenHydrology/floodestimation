# -*- coding: utf-8 -*-

from floodestimation import db
from floodestimation.entities import Catchment, Descriptors, AmaxRecord
from floodestimation.analysis import QmedAnalysis
from floodestimation.collections import CatchmentCollections
import numpy as np
from sqlalchemy import or_
from sqlalchemy.sql.functions import func

db_session = db.Session()
gauged_catchments = CatchmentCollections(db_session)
rural_catchments = db_session.query(Catchment).join(Descriptors).join(Catchment.amax_records). \
    filter(Catchment.is_suitable_for_qmed,
           Descriptors.centroid_ngr != None,
           or_(Descriptors.urbext2000 < 0.03, Descriptors.urbext2000 == None)). \
    group_by(Catchment). \
    having(func.count(AmaxRecord.catchment_id) > 2). \
    all()
n = len(rural_catchments)
print("Total number of rural catchments: {}".format(n))

ids = np.empty(n)
qmed_amax = np.empty(n)
qmed_descr = np.empty(n)
qmed_descr_idw1 = np.empty(n)
qmed_descr_idw2 = np.empty(n)
qmed_descr_first = np.empty(n)

for i, c in enumerate(rural_catchments):
    print(i, c.id)
    ids[i] = c.id
    analysis = QmedAnalysis(c)
    try:
        qmed_amax[i] = analysis.qmed(method='amax_records')
    except:
        pass
    qmed_descr[i] = analysis.qmed(method='descriptors')
    analysis.gauged_catchments = gauged_catchments
    qmed_descr_idw2[i] = analysis.qmed(method='descriptors')
    analysis.idw_power = 1
    qmed_descr_idw1[i] = analysis.qmed(method='descriptors')
    analysis.donor_weighting = 'first'
    qmed_descr_first[i] = analysis.qmed(method='descriptors')

np.savetxt('output.txt', (ids, qmed_amax, qmed_descr, qmed_descr_idw2, qmed_descr_first, qmed_descr_idw1), delimiter=',')

db_session.close()