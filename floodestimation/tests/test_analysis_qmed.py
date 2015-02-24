import unittest
import os
from numpy.testing import assert_almost_equal, assert_array_almost_equal_nulp
from urllib.request import pathname2url
from datetime import date
from floodestimation.entities import Catchment, AmaxRecord, Descriptors, Point, PotDataset, PotRecord, PotDataGap
from floodestimation.collections import CatchmentCollections
from floodestimation import db
from floodestimation import settings
from floodestimation.analysis import QmedAnalysis, InsufficientDataError
from math import exp

class TestCatchmentQmed(unittest.TestCase):
    def test_channel_width_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='channel_width'), 0.182)

    def test_channel_width_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 2.345
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='channel_width'), 0.9839, 4)

    def test_channel_width_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 50
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='channel_width'), 420.7576, 4)

    def test_channel_no_width(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            QmedAnalysis(catchment).qmed(method='channel_width')
        except InsufficientDataError as e:
            self.assertEqual(str(e), "Catchment `channel_width` attribute must be set first.")

    def test_area_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.dtm_area = 1
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='area'), 1.172)

    def test_area_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.dtm_area = 2.345
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='area'), 2.6946, 4)

    def test_area_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.dtm_area = 100
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='area'), 81.2790, 4)

    def test_no_area(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            QmedAnalysis(catchment).qmed(method='area')
        except InsufficientDataError as e:
            self.assertEqual(str(e), "Catchment `descriptors` attribute must be set first.")

    def test_descriptors_1999_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=0)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_1999'), 0.2671, 4)

    def test_descriptors_1999_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=2.345,
                                            bfihost=0,
                                            sprhost=100,
                                            saar=2000,
                                            farl=0.5,
                                            urbext2000=0)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_1999'), 0.3729, 4)

    def test_descriptors_1999_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=100,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=0)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_1999'), 18.5262, 4)

    def test_no_descriptors_1999(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            QmedAnalysis(catchment).qmed(method='descriptors_1999')
        except InsufficientDataError as e:
            self.assertEqual(str(e), "Catchment `descriptors` attribute must be set first.")

    def test_descriptors_2008_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=0)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_2008'), 0.5907, 4)

    def test_descriptors_2008_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=2.345,
                                            bfihost=0,
                                            sprhost=100,
                                            saar=2000,
                                            farl=0.5,
                                            urbext2000=0)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_2008'), 0.6173, 4)

    def test_descriptors_2008_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=100,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=0)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_2008'),  29.7432, 4)

    def test_descriptors_2008_rural(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=1)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_2008', as_rural=True), 0.5907, 4)

    def test_descriptors_2008_urban_adjustment(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=1)
        self.assertAlmostEqual(QmedAnalysis(catchment, year=2000).urban_adj_factor(), 2.970205798, 4)

    def test_descriptors_2008_urban(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=1)
        self.assertAlmostEqual(QmedAnalysis(catchment, year=2000).qmed(method='descriptors_2008', as_rural=False),
                               1.7546, 4)

    def test_no_descriptors_2008(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            QmedAnalysis(catchment).qmed(method='descriptors_2008')
        except InsufficientDataError as e:
            self.assertEqual(str(e), "Catchment `descriptors` attribute must be set first.")

    def test_descriptors_alias(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=1)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors', as_rural=True), 0.5907, 4)

    def test_amax_odd_records(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 3.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2001, 12, 31), 1.0, 0.5)]
        self.assertEqual(QmedAnalysis(catchment).qmed(method='amax_records'), 2)

    def test_amax_even_records(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        self.assertEqual(QmedAnalysis(catchment).qmed(method='amax_records'), 1.5)

    def test_amax_rejected_record(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 99.0, 0.5, flag=2)]
        self.assertEqual(QmedAnalysis(catchment).qmed(method='amax_records'), 1.5)

    def test_amax_long_records(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 5.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2001, 12, 31), 4.0, 0.5),
                                  AmaxRecord(date(2002, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2003, 12, 31), 3.0, 0.5)]
        self.assertEqual(QmedAnalysis(catchment).qmed(method='amax_records'), 3)

    def test_pot_1_year(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.pot_dataset = PotDataset(start_date=date(1999, 1, 1), end_date=date(1999, 12, 31))
        catchment.pot_dataset.pot_records = [PotRecord(date(1999, 1, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5)]
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='pot_records'), 1.6696)

    def test_pot_2_years(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.pot_dataset = PotDataset(start_date=date(1998, 1, 1), end_date=date(1999, 12, 31))
        catchment.pot_dataset.pot_records = [PotRecord(date(1999, 1, 1), 3.0, 0.5),
                                             PotRecord(date(1999, 2, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5)]
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='pot_records'), 1.8789, 4)

    def test_pot_records_by_month(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.pot_dataset = PotDataset(start_date=date(1998, 10, 1), end_date=date(2000, 1, 31))
        catchment.pot_dataset.pot_records = [PotRecord(date(1999, 1, 1), 3.0, 0.5),
                                             PotRecord(date(1999, 2, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 2, 15), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5)]
        analysis = QmedAnalysis(catchment)
        records_by_month = analysis._pot_month_counts(catchment.pot_dataset)
        expected = [2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
        result = [len(month) for month in records_by_month]
        self.assertEqual(result, expected)

    def test_pot_complete_years(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.pot_dataset = PotDataset(start_date=date(1998, 10, 1), end_date=date(2000, 1, 31))
        catchment.pot_dataset.pot_records = [PotRecord(date(1999, 1, 1), 3.0, 0.5),
                                             PotRecord(date(1999, 2, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 2, 15), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5)]
        analysis = QmedAnalysis(catchment)
        records, n = analysis._complete_pot_years(catchment.pot_dataset)
        result = [record.date for record in records]
        expected = [date(1999, 2, 1),
                    date(1999, 2, 15),
                    date(1999, 12, 31)]
        self.assertEqual(result, expected)

    def test_pot_complete_years_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.pot_dataset = PotDataset(start_date=date(1998, 10, 1), end_date=date(2000, 1, 31))
        catchment.pot_dataset.pot_records = [PotRecord(date(1998, 10, 1), 3.0, 0.5),
                                             PotRecord(date(1999, 1, 1), 3.0, 0.5),
                                             PotRecord(date(1999, 2, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 2, 15), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5),
                                             PotRecord(date(2000, 1, 5), 1.0, 0.5)]
        analysis = QmedAnalysis(catchment)
        records, n = analysis._complete_pot_years(catchment.pot_dataset)
        result = [record.date for record in records]
        expected = [date(1999, 2, 1),
                    date(1999, 2, 15),
                    date(1999, 12, 31),
                    date(2000, 1, 5)]
        self.assertEqual(result, expected)

    def test_all(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=0)
        qmeds = QmedAnalysis(catchment).qmed_all_methods()
        self.assertEqual(qmeds['amax_records'], 1)
        self.assertEqual(qmeds['channel_width'], 0.182)
        self.assertEqual(qmeds['area'], 1.172)
        self.assertAlmostEqual(qmeds['descriptors_1999'], 0.2671, 4)

    def test_best_method_none(self):
        catchment = Catchment("Aberdeen", "River Dee")
        self.assertIsNone(catchment.qmed())

    def test_best_method_channel_width(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        self.assertEqual(catchment.qmed(), 0.182)

    def test_best_method_area(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1)
        self.assertEqual(catchment.qmed(), 1.172)

    def test_best_method_descriptors(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=0)
        self.assertAlmostEqual(catchment.qmed(), 0.5907, 4)

    def test_best_method_amax(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        self.assertEqual(catchment.qmed(), 1.0)

    def test_best_method_pot(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.pot_dataset = PotDataset(start_date=date(1999, 1, 1), end_date=date(1999, 12, 31))

        catchment.pot_dataset.pot_records = [PotRecord(date(1999, 1, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5)]
        self.assertAlmostEqual(catchment.qmed(), 1.6696)

    def test_best_method_pot_over_amax(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        catchment.pot_dataset = PotDataset(start_date=date(1998, 1, 1), end_date=date(1999, 12, 31))
        catchment.pot_dataset.pot_records = [PotRecord(date(1999, 1, 1), 3.0, 0.5),
                                             PotRecord(date(1999, 2, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5)]
        self.assertAlmostEqual(catchment.qmed(), 1.8789, 4)

    def test_best_method_amax_over_pot(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        catchment.pot_dataset = PotDataset(start_date=date(1999, 1, 1), end_date=date(1999, 12, 31))
        catchment.pot_dataset.pot_records = [PotRecord(date(1999, 1, 1), 3.0, 0.5),
                                             PotRecord(date(1999, 2, 1), 2.0, 0.5),
                                             PotRecord(date(1999, 12, 31), 1.0, 0.5)]
        self.assertAlmostEqual(catchment.qmed(), 1.5)

    def test_best_method_order(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1)
        self.assertEqual(catchment.qmed(), 1.0)

    def test_unsupported_method(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            QmedAnalysis(catchment).qmed(method='abc')
        except AttributeError as e:
            self.assertEqual(str(e), "Method `abc` to estimate QMED does not exist.")


class TestQmedDonor(unittest.TestCase):
    catchment = Catchment("Dundee", "River Tay")
    catchment.country = 'gb'
    catchment.descriptors = Descriptors(dtm_area=2.345,
                                        bfihost=1e-4,
                                        sprhost=100,
                                        saar=2000,
                                        farl=0.5,
                                        urbext2000=0,
                                        centroid_ngr=Point(276125, 688424))
    # QMED descr = 0.61732109

    donor_catchment = Catchment("Aberdeen", "River Dee")
    donor_catchment.country = 'gb'
    donor_catchment.descriptors = Descriptors(dtm_area=1,
                                              bfihost=0.50,
                                              sprhost=50,
                                              saar=1000,
                                              farl=1,
                                              urbext2000=0,
                                              centroid_ngr=Point(276125, 688424))
    donor_catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                    AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
    # donor QMED descr = 0.59072777
    # donor QMED amax = 1.0

    @classmethod
    def setUpClass(cls):
        settings.config['nrfa']['oh_json_url'] = \
            'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))
        cls.db_session = db.Session()

    @classmethod
    def tearDownClass(cls):
        db.empty_db_tables()

    def tearDown(self):
        self.db_session.rollback()

    def test_donor_adjustment_factor(self):
        # 1.0/0.59072777 = 1.69282714
        self.assertAlmostEqual(exp(QmedAnalysis(self.catchment).
                                   _lnqmed_residual(self.donor_catchment)), 1.69282714)

    def test_lnqmed_residual_one_donor(self):
        # ln(1.0 / 0.59072777)
        self.assertAlmostEqual(QmedAnalysis(self.catchment).
                               _lnqmed_residual(self.donor_catchment), 0.5264, 4)

    def test_model_error_corr(self):
        # because we're at zero distance, error correlation = 1
        self.assertAlmostEqual(QmedAnalysis(self.catchment).
                               _model_error_corr(self.catchment, self.donor_catchment), 1)

    def test_vector_b_one_donor(self):
        assert_almost_equal(QmedAnalysis(self.catchment).
                            _vec_b([self.donor_catchment]), [0.1175])

    def test_matrix_sigma_eta_one_donor(self):
        result = QmedAnalysis(self.catchment)._matrix_sigma_eta([self.donor_catchment])
        assert_almost_equal(result, [[0.1175]])

    def test_beta_one_donor(self):
        result = QmedAnalysis(self.catchment)._beta(self.donor_catchment)
        self.assertAlmostEqual(result, 0.30242554)

    def test_matrix_sigma_eps_one_donor(self):
        # 4 * 0.30242554**2 / 2 = 0.18292242
        result = QmedAnalysis(self.catchment)._matrix_sigma_eps([self.donor_catchment])
        assert_almost_equal(result, [[0.18292242]])

    def test_matrix_omega_one_donor(self):
        # 0.1175 + 0.18292242 = 0.30042242
        result = QmedAnalysis(self.catchment)._matrix_omega([self.donor_catchment])
        assert_almost_equal(result, [[0.30042242]])

    def test_vector_alpha_one_donor(self):
        # 1/0.30042242 * 0.1175 = 0.39111595
        result = QmedAnalysis(self.catchment)._vec_alpha([self.donor_catchment])
        assert_almost_equal(result, [0.39111595])

    def test_qmed_one_donor(self):
        # 0.61732109 * 1.69282714**0.39111595 = 0.75844685
        result = QmedAnalysis(self.catchment).qmed(method='descriptors', donor_catchments=[self.donor_catchment])
        self.assertAlmostEqual(result, 0.75844685, places=4)

    def test_distance_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        result = [d.distance_to(self.catchment) for d in donors]
        assert_almost_equal(result, [5, 183.8515], decimal=4)

    def test_lnqmed_residuals_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        qmed_amax = [QmedAnalysis(d).qmed() for d in donors]
        qmed_descr =[QmedAnalysis(d, year=2000).qmed(method='descriptors') for d in donors]
        assert_almost_equal(qmed_amax, [90.532, 50.18])  # not verified
        assert_almost_equal(qmed_descr, [51.73180402, 48.70106637])  # not verified

        result = [analysis._lnqmed_residual(d) for d in donors]
        assert_almost_equal(result, [0.55963062, 0.02991561])

    def test_model_error_corr_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        result = [analysis._model_error_corr(self.catchment, d) for d in donors]
        assert_almost_equal(result, [0.352256808, 0.002198921])

    def test_model_error_corr_between_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        dist = donors[0].distance_to(donors[1])
        self.assertAlmostEqual(dist, 188.8487072)  # not verified

        result = analysis._model_error_corr(donors[0], donors[1])
        self.assertAlmostEqual(result, 0.001908936)

    def test_vector_b_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        # [0.352256808, 0.002198921] * 0.1175 = [0.041390175, 0.000258373]
        result = analysis._vec_b(donors)
        assert_almost_equal(result, [0.041390175, 0.000258373])

    def test_matrix_sigma_eta_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        result = analysis._matrix_sigma_eta(donors)
        # 0.1175 * 0.001908936 = 0.00022430
        assert_almost_equal(result, [[0.1175, 0.00022430],
                                     [0.00022430, 0.1175]])

    def test_beta_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        result = [analysis._beta(d) for d in donors]
        assert_almost_equal(result, [0.16351290, 0.20423656])

    def test_lnqmed_corr(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        results = analysis._lnqmed_corr(donors[0], donors[1])
        self.assertAlmostEqual(results, 0.133632774)

    def test_matrix_sigma_eps_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        record0 = [donors[0].amax_records_start(), donors[0].amax_records_end()]
        record1 = [donors[1].amax_records_start(), donors[1].amax_records_end()]
        self.assertEqual(record0, [1969, 2005])  # n=37
        self.assertEqual(record1, [1939, 1984])  # n=46, 16 years overlapping

        result = analysis._matrix_sigma_eps(donors)
        # 4 * 0.16351290**2 / 37 = 0.00289043
        # 4 * 0.16351290 * 0.20423656 * 16 / 37 / 46 * 0.133632774 = 0.00016781
        # 4 * 0.20423656**2 / 46 = 0.00362718
        assert_almost_equal(result, [[0.00289043, 0.00016781],
                                     [0.00016781, 0.00362718]])

    def test_matrix_omega_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001
        result = analysis._matrix_omega(donors)
        assert_almost_equal(result, [[0.12039043, 0.00039211],
                                     [0.00039211, 0.12112718]])

    def test_vector_alpha_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001
        result = analysis._vec_alpha(donors)
        assert_almost_equal(result, [0.34379622, 0.00102012])  # calculated in Excel

    def test_qmed_two_donors(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        donors = analysis.find_donor_catchments()[0:2]  # 17001, 10001

        result = analysis.qmed(method='descriptors', donor_catchments=donors)

        # exp(ln(0.61732109) + 0.34379622 * 0.55963062 + 0.00102012 * 0.02991561) =
        # exp(ln(0.61732109) + 0.192429411) = 0.748311028
        self.assertAlmostEqual(result, 0.748311028, places=5)
