import unittest
import os
from numpy.testing import assert_almost_equal
from urllib.request import pathname2url
from datetime import date
from floodestimation.entities import Catchment, AmaxRecord, Descriptors, Point, PotDataset, PotRecord, PotDataGap
from floodestimation.collections import CatchmentCollections
from floodestimation import db
from floodestimation import settings
from floodestimation.analysis import QmedAnalysis, InsufficientDataError


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
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_2008'), 0.5909, 4)

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
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_2008'), 29.7497, 4)

    def test_descriptors_2008_rural(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext2000=1)
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors_2008', as_rural=True), 0.5909, 4)

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
                               1.754969605, 4)

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
        self.assertAlmostEqual(QmedAnalysis(catchment).qmed(method='descriptors', as_rural=True), 0.5909, 4)

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
        result =[len(month) for month in records_by_month]
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
        self.assertAlmostEqual(catchment.qmed(), 0.5909, 4)

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
                                        bfihost=0.0,
                                        sprhost=100,
                                        saar=2000,
                                        farl=0.5,
                                        urbext2000=0,
                                        centroid_ngr=Point(276125, 688424))
    # QMED descr = 0.6173210932631318

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
    # donor QMED descr = .5909
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
        # 1.0/ 0.5909
        self.assertAlmostEqual(QmedAnalysis(self.catchment)._donor_adj_factor(self.donor_catchment), 1.6925, 4)

    def test_donor_corrected_qmed(self):
        # 0.6173 * 1.6925
        self.assertAlmostEqual(
            QmedAnalysis(self.catchment).qmed(method='descriptors_2008', donor_catchments=[self.donor_catchment]),
            1.0448, places=4)

    def test_first_automatic_donor_qmed(self):

        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)

        # Use the first donor only!
        donor = analysis.find_donor_catchments()[0]
        # donor: qmed_am = 90.532, qmed_cd = 51.73814611333827
        self.assertEqual(17001, donor.id)
        self.assertEqual(5, donor.distance_to(self.catchment))
        self.assertAlmostEqual(0.4654, analysis._error_corr(donor), places=4)
        assert_almost_equal([1.2974563], analysis._donor_adj_factors([donor]), decimal=7)
        assert_almost_equal([1], analysis._donor_weights([donor]))
        # 0.6173210932631318 * 1.2974563 = 0.8009471415771379
        self.assertAlmostEqual(0.800947, analysis.qmed(donor_catchments=[donor]), places=4)

    def test_two_automatic_donor_qmed(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)

        # Use the first 2 donors
        donors = analysis.find_donor_catchments()[0:2]

        self.assertAlmostEqual(5, donors[0].distance_to(self.catchment), places=4)
        self.assertAlmostEqual(183.8515, donors[1].distance_to(self.catchment), places=4)
        assert_almost_equal([1.2974563, 1.0003], analysis._donor_adj_factors(donors), decimal=4)
        assert_almost_equal([0.9999799, 0.0000201], analysis._donor_weights(donors), decimal=7)

        self.assertAlmostEqual(0.80094, analysis.qmed(donor_catchments=donors), places=4)

    def test_two_automatic_donor_qmed_linear_idw(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        analysis.idw_power = 1

        # Use the first 2 donors
        donors = analysis.find_donor_catchments()[0:2]
        assert_almost_equal([0.9735, 0.0265], analysis._donor_weights(donors), decimal=4)

        self.assertAlmostEqual(0.7961, analysis.qmed(donor_catchments=donors), places=4)

    def test_two_automatic_donor_qmed_equal_weight(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        analysis.donor_weighting = 'equal'

        # Use the first 2 donors
        donors = analysis.find_donor_catchments()[0:2]

        self.assertAlmostEqual(5, donors[0].distance_to(self.catchment), places=4)
        self.assertAlmostEqual(183.8515, donors[1].distance_to(self.catchment), places=4)
        assert_almost_equal([1.2974563, 1.0003], analysis._donor_adj_factors(donors), decimal=4)
        assert_almost_equal([0.5, 0.5], analysis._donor_weights(donors), decimal=4)

        self.assertAlmostEqual(0.7092267, analysis.qmed(donor_catchments=donors), places=4)

    def test_two_automatic_donor_qmed_first_weight(self):
        analysis = QmedAnalysis(self.catchment, CatchmentCollections(self.db_session), year=2000)
        analysis.donor_weighting = 'first'

        # Use the first 2 donors
        donors = analysis.find_donor_catchments()[0:2]

        self.assertAlmostEqual(5, donors[0].distance_to(self.catchment), places=4)
        self.assertAlmostEqual(183.8515, donors[1].distance_to(self.catchment), places=4)
        assert_almost_equal([1.2974563, 1.0003], analysis._donor_adj_factors(donors), decimal=4)
        assert_almost_equal([1, 0], analysis._donor_weights(donors), decimal=4)

        self.assertAlmostEqual(0.800947, analysis.qmed(donor_catchments=donors), places=4)
