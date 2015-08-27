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
        cls.session = db.Session()

    def setUp(self):
        settings.config['nrfa']['oh_json_url'] = \
            'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def test_load_catchment(self):
        catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        self.assertEqual(17002, catchment.id)
        self.assertEqual(4, len(catchment.amax_records))
        self.assertEqual(146, len(catchment.pot_dataset.pot_records))

    def test_load_catchment_without_amax(self):
        catchment = loaders.from_file('floodestimation/tests/data/170021.CD3')
        self.assertEqual([], catchment.amax_records)

    def test_load_catchment_from_xml(self):
        catchment = loaders.from_file('floodestimation/tests/data/NN 04000 48400.xml')
        self.assertEqual(catchment.area, 30.09)
        self.assertEqual([], catchment.amax_records)

    def test_add_catchment_twice(self):
        catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        loaders.to_db(catchment, self.session)

        duplicate_catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        loaders.to_db(duplicate_catchment, self.session)
        self.assertRaises(IntegrityError, self.session.flush)

        self.session.rollback()

    def test_update_catchment(self):
        catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        # Make a change
        catchment.location = "Dundee"
        loaders.to_db(catchment, self.session)

        # Reload catchment again
        duplicate_catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        loaders.to_db(duplicate_catchment, self.session, method='update')
        self.session.flush()

        # Should have original data
        self.assertEqual(self.session.query(Catchment).get(17002).location, "Leven")

        self.session.rollback()

    def test_save_catchments_to_db(self):
        loaders.nrfa_to_db(self.session)
        expected = ['Ardlethen', "Curry's Bridge", 'Dudgeon Bridge', 'Headswood', 'Inverugie', 'Leven']
        result = [catchment.location for catchment in self.session.query(Catchment).order_by(Catchment.location).all()]
        self.assertEqual(expected, result)
        self.session.rollback()

    def test_userdata_to_db(self):
        loaders.nrfa_to_db(self.session)

        settings.config['import']['folder'] = 'floodestimation/tests/data'
        loaders.userdata_to_db(self.session)
        self.assertEqual(self.session.query(Catchment).count(), 9)

        self.session.rollback()
