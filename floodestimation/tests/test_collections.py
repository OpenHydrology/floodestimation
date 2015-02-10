# -*- coding: utf-8 -*-

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
        settings.config['nrfa']['oh_json_url'] = \
            'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
        cls.db_session = db.Session()
        db.empty_db_tables()

    def tearDown(self):
        self.db_session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.db_session.close()
        db.empty_db_tables()

    def test_catchment_by_number(self):
        expected = loaders.from_file('floodestimation/tests/data/17002.CD3')
        self.db_session.add(expected)

        result = CatchmentCollections(self.db_session).catchment_by_number(17002)
        self.assertIs(expected, result)

    def test_catchment_by_number_not_exist(self):
        result = CatchmentCollections(self.db_session, load_data='manual').catchment_by_number(99)
        self.assertIsNone(result)

    def test_nearest_catchments(self):
        subject_catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        catchments = CatchmentCollections(self.db_session).nearest_qmed_catchments(subject_catchment)
        result = [catchment.id for catchment in catchments]
        expected = [17001, 10001, 10002]
        self.assertEqual(expected, result)

    def test_most_similar_catchments(self):
        subject_catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        # Dummy similarity distance function
        function = lambda c1, c2: abs(c2.descriptors.altbar - c1.descriptors.altbar)
        catchments = CatchmentCollections(self.db_session).most_similar_catchments(subject_catchment, function)
        result = [c.id for c in catchments]
        expected = [10001, 10002]
        self.assertEqual(expected, result)

    def test_incl_subject_catchment(self):
        # Subject catchment not in db
        subject_catchment = loaders.from_file('floodestimation/tests/data/37017.CD3')
        # Dummy similarity distance function
        function = lambda c1, c2: abs(c2.descriptors.altbar - c1.descriptors.altbar)
        catchments = CatchmentCollections(self.db_session).most_similar_catchments(subject_catchment, function,
                                                                                   include_subject_catchment='force')
        result = [c.id for c in catchments]
        expected = [37017, 10002, 10001]
        self.assertEqual(expected, result)
        self.assertEqual(catchments[0].similarity_dist, 0)

    def test_incl_subject_catchment_updated(self):
        # Subject catchment in db
        subject_catchment = loaders.from_file('floodestimation/tests/data/201002.CD3')
        subject_catchment.location = "Updated location name"
        # Dummy similarity distance function
        function = lambda c1, c2: abs(c2.descriptors.altbar - c1.descriptors.altbar)
        catchments = CatchmentCollections(self.db_session).most_similar_catchments(subject_catchment, function,
                                                                                   include_subject_catchment='force')
        result = [c.id for c in catchments]
        expected = [201002, 10001, 10002]
        self.assertEqual(expected, result)
        self.assertEqual(catchments[0].location, "Updated location name")

    def test_invalid_subj_catchment_option(self):
        subject_catchment = loaders.from_file('floodestimation/tests/data/17002.CD3')
        # Dummy similarity distance function
        function = lambda c1, c2: abs(c2.descriptors.altbar - c1.descriptors.altbar)
        self.assertRaises(ValueError, CatchmentCollections(self.db_session).most_similar_catchments,
                          subject_catchment, function, include_subject_catchment='invalid')
