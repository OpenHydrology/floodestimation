import unittest
import os
from urllib.request import pathname2url
from floodestimation import db
from floodestimation import loaders
from floodestimation import settings
from floodestimation.collections import CatchmentCollections

class TestCatchmentCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.OPEN_HYDROLOGY_JSON_URL = 'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
        cls.db_session = db.Session()

    @classmethod
    def tearDownClass(cls):
        cls.db_session.rollback()
        cls.db_session.close()

    def test_catchment_by_number(self):
        expected = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        self.db_session.add(expected)

        result = CatchmentCollections(self.db_session).catchment_by_number(17002)
        self.assertIs(expected, result)

        self.db_session.rollback()

    def test_catchment_by_number_not_exist(self):
        result = CatchmentCollections(self.db_session).catchment_by_number(99)
        self.assertIsNone(result)

    def test_nearest_catchments(self):
        loaders.gauged_catchments_to_db(self.db_session)

        subject_catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        catchments = CatchmentCollections(self.db_session).nearest_qmed_catchments(subject_catchment)
        result = [catchment.id for catchment in catchments]
        expected = [17001, 10001, 10002, 201002]
        self.assertEqual(expected, result)

        self.db_session.rollback()