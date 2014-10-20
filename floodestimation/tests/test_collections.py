# -*- coding: utf-8 -*-

import unittest
import os
from urllib.request import pathname2url
from floodestimation import db
from floodestimation import loaders
from floodestimation import settings
from floodestimation.collections import CatchmentCollections
from floodestimation.entities import Catchment


class TestCatchmentCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.OPEN_HYDROLOGY_JSON_URL = 'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
        cls.db_session = db.Session()

    def tearDown(self):
        self.db_session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.db_session.close()
        db.reset_db_tables()

    def test_catchment_by_number(self):
        expected = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        self.db_session.add(expected)

        result = CatchmentCollections(self.db_session).catchment_by_number(17002)
        self.assertIs(expected, result)

    def test_catchment_by_number_not_exist(self):
        result = CatchmentCollections(self.db_session, load_data='manual').catchment_by_number(99)
        self.assertIsNone(result)

    def test_nearest_catchments(self):
        subject_catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        catchments = CatchmentCollections(self.db_session).nearest_qmed_catchments(subject_catchment)
        result = [catchment.id for catchment in catchments]
        expected = [17001, 10001, 10002]
        self.assertEqual(expected, result)

    def test_most_similar_catchments(self):
        subject_catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        # Dummy similarity distance function
        function = lambda c1, c2: c2.descriptors.altbar - c1.descriptors.altbar
        catchments = CatchmentCollections(self.db_session).most_similar_catchments(subject_catchment, function)
        result = [c.id for c in catchments]
        expected = [10002, 10001]
        self.assertEqual(expected, result)

