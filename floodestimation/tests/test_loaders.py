# -*- coding: utf-8 -*-

import unittest
import os
from urllib.request import pathname2url
from floodestimation import db
from floodestimation import loaders
from floodestimation import settings
from floodestimation.entities import Catchment


class TestLoaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.OPEN_HYDROLOGY_JSON_URL = 'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
        cls.session = db.Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def test_load_catchment(self):
        catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        self.assertEqual(17002, catchment.id)
        self.assertEqual(4, len(catchment.amax_records))
        self.assertEqual(146, len(catchment.pot_dataset.pot_records))

    def test_load_catchment_without_amax(self):
        catchment = loaders.load_catchment('floodestimation/tests/data/170021.CD3')
        self.assertEqual([], catchment.amax_records)

    def test_save_catchments_to_db(self):
        loaders.gauged_catchments_to_db(self.session)
        expected = ['Ardlethen', "Curry's Bridge", 'Dudgeon Bridge', 'Headswood', 'Inverugie', 'Leven']
        result = [catchment.location for catchment in self.session.query(Catchment).order_by(Catchment.location).all()]
        self.assertEqual(expected, result)
        self.session.rollback()
