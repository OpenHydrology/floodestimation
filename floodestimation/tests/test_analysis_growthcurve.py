# -*- coding: utf-8 -*-

import unittest
import os
import lmoments3 as lm
import numpy as np
from copy import copy
from numpy.testing import assert_almost_equal
from datetime import date
from urllib.request import pathname2url
from floodestimation.entities import Catchment, Descriptors, AmaxRecord, Point
from floodestimation.analysis import GrowthCurveAnalysis
from floodestimation import db
from floodestimation import settings
from floodestimation.collections import CatchmentCollections
from floodestimation.loaders import load_catchment


class TestGrowthCurveAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.config['nrfa']['oh_json_url'] = \
            'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
        cls.db_session = db.Session()

        cls.catchment = Catchment("Dundee", "River Tay")
        cls.catchment.country = 'gb'
        cls.catchment.descriptors = Descriptors(dtm_area=2.345,
                                                bfihost=0.0,
                                                sprhost=100,
                                                saar=2000,
                                                farl=0.5,
                                                urbext2000=0,
                                                fpext=0.2,
                                                centroid_ngr=Point(276125, 688424))

    def tearDown(self):
        self.db_session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.db_session.close()
        db.empty_db_tables()

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

    def test_single_site_glo(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(catchment, gauged_catchments)
        dist_func = analysis.growth_curve(method='single_site', distr='glo')
        self.assertAlmostEqual(dist_func(0.5), 1)

    def test_single_site_gev(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(catchment, gauged_catchments)
        dist_func = analysis.growth_curve(method='single_site', distr='gev')
        self.assertAlmostEqual(dist_func(0.5), 1)

    def test_l_cv_and_skew(self):
        gauged_catchments = CatchmentCollections(self.db_session)
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment, gauged_catchments)
        var, skew = analysis._var_and_skew(catchment)

        self.assertAlmostEqual(var, 0.2232, places=4)
        self.assertAlmostEqual(skew, -0.0908, places=4)

    def test_l_cv_and_skew_one_donor_rural(self):
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment, year=2000)
        analysis.donor_catchments = [catchment]
        var, skew = analysis._var_and_skew(analysis.donor_catchments, as_rural=True)

        self.assertAlmostEqual(var, 0.2232, places=4)
        self.assertAlmostEqual(skew, -0.0908, places=4)

    def test_l_cv_and_skew_one_donor_urban(self):
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment, year=2000)
        analysis.donor_catchments = [catchment]
        var, skew = analysis._var_and_skew(analysis.donor_catchments)

        self.assertAlmostEqual(var, 0.21987, places=4)
        self.assertAlmostEqual(skew, -0.08746, places=4)

    def test_37017(self):
        subject = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(subject)
        self.assertEqual(len(subject.amax_records), 34)
        var, skew = analysis._var_and_skew(subject)
        self.assertAlmostEqual(var, 0.2232, places=4)
        self.assertAlmostEqual(skew, -0.0908, places=4)

    def test_dist_params(self):
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment)
        growth_curve = analysis.growth_curve(method='single_site')
        params = growth_curve.params

        self.assertAlmostEqual(params['loc'], 1)
        self.assertAlmostEqual(params['scale'], 0.2202, places=4)
        self.assertAlmostEqual(params['k'], 0.0908, places=4)
        # Kurtosis calculated from L-skew using eqns on
        # http://researcher.watson.ibm.com/researcher/view_group.php?id=2639
        self.assertAlmostEqual(growth_curve.distr_kurtosis, 0.1735, places=4)

    def test_dist_param_location(self):
        catchment = load_catchment('floodestimation/tests/data/37017.CD3')

        analysis = GrowthCurveAnalysis(catchment)
        growth_curve = analysis.growth_curve(method='single_site')
        self.assertAlmostEqual(growth_curve(0.5), 1)

    def test_dimensionless_flows(self):
        analysis = GrowthCurveAnalysis(self.catchment)
        self.catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 3.0, 0.5),
                                       AmaxRecord(date(2000, 12, 31), 2.0, 0.5),
                                       AmaxRecord(date(2001, 12, 31), 1.0, 0.5)]
        result = analysis._dimensionless_flows(self.catchment)
        expected = np.array([1.5, 1, 0.5])
        assert_almost_equal(result, expected)

    def test_l_cv_weight_same_catchment(self):
        subject = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(subject)
        result = analysis._l_cv_weight(subject)
        expected = 515.30  # Science Report SC050050, table 6.6, row 1
        self.assertAlmostEqual(result, expected, places=1)

    def test_l_cv_weight(self):
        subject = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(subject)
        donor = copy(subject)
        donor.similarity_dist = 0.2010
        result = analysis._l_cv_weight(donor)
        expected = 247.06  # Science Report SC050050, table 6.6, row 4 (note that donor has same record length as subject)
        self.assertAlmostEqual(result, expected, places=1)

    def test_l_skew_weight_same_catchment(self):
        subject = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(subject)
        result = analysis._l_skew_weight(subject)
        expected = 116.66  # Science Report SC050050, table 6.6, row 1
        self.assertAlmostEqual(result, expected, places=1)

    def test_l_skew_weight(self):
        subject = load_catchment('floodestimation/tests/data/37017.CD3')
        analysis = GrowthCurveAnalysis(subject)
        donor = copy(subject)
        donor.similarity_dist = 0.2010
        result = analysis._l_skew_weight(donor)
        expected = 47.34  # Science Report SC050050, table 6.6, row 4 (note that donor has same record length as subject)
        self.assertAlmostEqual(result, expected, places=1)

    def test_similarity_dist(self):
        subject = load_catchment('floodestimation/tests/data/37017.CD3')
        donor = load_catchment('floodestimation/tests/data/37020.CD3')
        analysis = GrowthCurveAnalysis(subject)
        result = analysis._similarity_distance(subject, donor)
        expected = 0.1159  # Science Report SC050050, table 6.6, row 2
        self.assertAlmostEqual(result, expected, places=4)