# -*- coding: utf-8 -*-

import unittest
import os
import lmoments3 as lm
from urllib.request import pathname2url
from floodestimation.entities import Catchment, Descriptors
from floodestimation.analysis import GrowthCurveAnalysis
from floodestimation import db
from floodestimation import settings
from floodestimation.collections import CatchmentCollections
from floodestimation.loaders import load_catchment


class TestGrowthCurveAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.OPEN_HYDROLOGY_JSON_URL = 'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
        cls.db_session = db.Session()

        cls.catchment = Catchment("Dundee", "River Tay")
        cls.catchment.country = 'gb'
        cls.catchment.descriptors = Descriptors(dtm_area=2.345,
                                                bfihost=0.0,
                                                sprhost=100,
                                                saar=2000,
                                                farl=0.5,
                                                urbext=0,
                                                fpext=0.2,
                                                centroid_ngr=(276125, 688424))

    def tearDown(self):
        self.db_session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.db_session.close()

    def test_find_donors_without_collection(self):
        analysis = GrowthCurveAnalysis(self.catchment)
        self.assertFalse(analysis.find_donor_catchments())

    def test_similarity_distance_incomplete_descriptors(self):
        other_catchment = Catchment(location="Burn A", watercourse="Village B")
        other_catchment.id = 999
        other_catchment.is_suitable_for_pooling = True
        self.db_session.add(other_catchment)

        gauged_catchments = CatchmentCollections(self.db_session)
        analysis = GrowthCurveAnalysis(self.catchment, gauged_catchments)
        self.assertEqual(float('inf'), analysis._similarity_distance(self.catchment, other_catchment))

    def test_find_donors_exclude_urban(self):
        other_catchment = Catchment(location="Burn A", watercourse="Village B")
        other_catchment.id = 999
        other_catchment.is_suitable_for_pooling = True
        other_catchment.descriptors = Descriptors(urbext2000=0.031)
        self.db_session.add(other_catchment)

        gauged_catchments = CatchmentCollections(self.db_session)
        analysis = GrowthCurveAnalysis(self.catchment, gauged_catchments)
        analysis.find_donor_catchments()
        donor_ids = [d.id for d in analysis.donor_catchments]
        self.assertEqual([10002, 10001], donor_ids)

    def test_find_donors(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        analysis = GrowthCurveAnalysis(self.catchment, gauged_catchments)
        analysis.find_donor_catchments()
        donor_ids = [d.id for d in analysis.donor_catchments]
        self.assertEqual([10002, 10001], donor_ids)

    def test_single_site(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(catchment, gauged_catchments)
        dist_func = analysis.growth_curve(method='single_site')
        self.assertAlmostEqual(dist_func(0.5), 1)

    def test_l_cv_and_skew(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment, gauged_catchments)
        var, skew = analysis._var_and_skew(catchment)

        self.assertAlmostEqual(var, 0.2232, places=4)
        self.assertAlmostEqual(skew, -0.0908, places=4)

    def test_l_cv_and_skew_one_donor(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment, gauged_catchments)
        analysis.donor_catchments = [catchment]
        var, skew = analysis._var_and_skew(analysis.donor_catchments)

        self.assertAlmostEqual(var, 0.2232, places=4)
        self.assertAlmostEqual(skew, -0.0908, places=4)

    def test_l_cv_and_skew_multiple_donors(self):
        # TODO
        pass

    def test_l_dist_params(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment, gauged_catchments)
        var, skew = analysis._var_and_skew(catchment)
        params = getattr(lm, 'pel' + 'glo')([1, var, skew])
        params[0] = 1

        self.assertAlmostEqual(params[0], 1, places=4)
        self.assertAlmostEqual(params[1], 0.2202, places=4)
        self.assertAlmostEqual(params[2], 0.0908, places=4)
