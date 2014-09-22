# -*- coding: utf-8 -*-

import unittest
import os
from urllib.request import pathname2url
from floodestimation.entities import Catchment, Descriptors
from floodestimation.analysis import GrowthCurveAnalysis
from floodestimation import db
from floodestimation import settings
from floodestimation.collections import CatchmentCollections

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

    def test_find_donors_incomplete_descriptors(self):
        other_catchment = Catchment(location="Burn A", watercourse="Village B")
        other_catchment.id = 999
        other_catchment.is_suitable_for_pooling = True
        self.db_session.add(other_catchment)

        gauged_catchments = CatchmentCollections(self.db_session)
        analysis = GrowthCurveAnalysis(self.catchment, gauged_catchments)
        self.assertEqual(float('inf'), analysis.find_donor_catchments()[2].similarity_dist)

    def test_find_donors_exclude_urban(self):
        other_catchment = Catchment(location="Burn A", watercourse="Village B")
        other_catchment.id = 999
        other_catchment.is_suitable_for_pooling = True
        other_catchment.descriptors = Descriptors(urbext2000=0.031)
        self.db_session.add(other_catchment)

        gauged_catchments = CatchmentCollections(self.db_session)
        analysis = GrowthCurveAnalysis(self.catchment, gauged_catchments)
        donor_ids = [d.id for d in analysis.find_donor_catchments()]
        self.assertEqual([10002, 10001], donor_ids)

    def test_find_donors(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        analysis = GrowthCurveAnalysis(self.catchment, gauged_catchments)
        donor_ids = [d.id for d in analysis.find_donor_catchments()]
        self.assertEqual([10002, 10001], donor_ids)