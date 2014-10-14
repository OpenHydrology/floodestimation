# -*- coding: utf-8 -*-

from floodestimation import db
from floodestimation.analysis import QmedAnalysis
from floodestimation.collections import CatchmentCollections


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
    result['qmed_descr_idw'] = analysis.qmed(method='descriptors', donor_catchments=donors)

    analysis.idw_power = 3
    result['qmed_descr_idw3'] = analysis.qmed(method='descriptors', donor_catchments=donors[0:10])

    analysis.donor_weighting = 'equal'
    result['qmed_descr_first'] = analysis.qmed(method='descriptors', donor_catchments=donors[0:1])

    return result


def science_report_catchment_ids():
    result = []
    with open(r'.\data\Science_report_stations.txt') as stations_file:
        for line in stations_file:
            result.append(int(line))
    return result


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
