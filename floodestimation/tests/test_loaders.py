# -*- coding: utf-8 -*-

import unittest
import os
from urllib.request import pathname2url
from floodestimation import db
from floodestimation import loaders
from floodestimation import settings
from floodestimation.entities import Catchment
from sqlalchemy.exc import IntegrityError


class TestLoaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.config['nrfa']['oh_json_url'] = \
            'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
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

    def test_add_catchment_twice(self):
        catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        self.session.add(catchment)

        duplicate_catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        self.session.add(duplicate_catchment)
        self.assertRaises(IntegrityError, self.session.flush)

        self.session.rollback()

    def test_update_catchment(self):
        catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        # Make a change
        catchment.location = "Dundee"
        self.session.add(catchment)

        # Reload catchment again
        duplicate_catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        loaders.update_catchment_in_db(duplicate_catchment, self.session)
        self.session.flush()

        # Should have original data
        self.assertEqual(self.session.query(Catchment).get(17002).location, "Leven")

        self.session.rollback()

    def test_save_catchments_to_db(self):
        loaders.gauged_catchments_to_db(self.session)
        expected = ['Ardlethen', "Curry's Bridge", 'Dudgeon Bridge', 'Headswood', 'Inverugie', 'Leven']
        result = [catchment.location for catchment in self.session.query(Catchment).order_by(Catchment.location).all()]
        self.assertEqual(expected, result)
        self.session.rollback()
