import unittest
from datetime import date
from floodestimation.entities import Catchment, AmaxRecord, Descriptors
from floodestimation.analysis import QmedAnalysis, InsufficientDataError


class TestCatchmentQmed(unittest.TestCase):
    def test_channel_width_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        self.assertEqual(QmedAnalysis(catchment).qmed(method='channel_width'), 0.182)

    def test_channel_width_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 2.345
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='channel_width'), 4), 0.9839)

    def test_channel_width_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 50
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='channel_width'), 4), 420.7576)

    def test_channel_no_width(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            QmedAnalysis(catchment).qmed(method='channel_width')
        except InsufficientDataError as e:
            self.assertEqual(str(e), "Catchment `channel_width` attribute must be set first.")

    def test_area_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.dtm_area = 1
        self.assertEqual(QmedAnalysis(catchment).qmed(method='area'), 1.172)

    def test_area_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.dtm_area = 2.345
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='area'), 4), 2.6946)

    def test_area_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.dtm_area = 100
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='area'), 4), 81.2790)

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
                                            urbext=0)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_1999'), 4), 0.2671)

    def test_descriptors_1999_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=2.345,
                                            bfihost=0,
                                            sprhost=100,
                                            saar=2000,
                                            farl=0.5,
                                            urbext=0)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_1999'), 4), 0.3729)

    def test_descriptors_1999_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=100,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext=0)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_1999'), 4), 18.5262)

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
                                            urbext=0)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_2008'), 4), 0.5909)

    def test_descriptors_2008_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=2.345,
                                            bfihost=0,
                                            sprhost=100,
                                            saar=2000,
                                            farl=0.5,
                                            urbext=0)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_2008'), 4), 0.6173)

    def test_descriptors_2008_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=100,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext=0)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_2008'), 4), 29.7497)

    def test_descriptors_2008_rural(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext=1)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_2008', as_rural=True), 4), 0.5909)

    def test_descriptors_2008_urban_adjustment(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext=1)
        self.assertEqual(round(QmedAnalysis(catchment).urban_adj_factor(), 4), 2.215)

    def test_descriptors_2008_urban(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = Descriptors(dtm_area=1,
                                            bfihost=0.50,
                                            sprhost=50,
                                            saar=1000,
                                            farl=1,
                                            urbext=1)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors_2008', as_rural=False), 4), 1.3087)

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
                                            urbext=1)
        self.assertEqual(round(QmedAnalysis(catchment).qmed(method='descriptors', as_rural=True), 4), 0.5909)

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

    def test_amax_long_records(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 5.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2001, 12, 31), 4.0, 0.5),
                                  AmaxRecord(date(2002, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2003, 12, 31), 3.0, 0.5)]
        self.assertEqual(QmedAnalysis(catchment).qmed(method='amax_records'), 3)

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
                                            urbext=0)
        qmeds = QmedAnalysis(catchment).qmed_all_methods()
        self.assertEqual(qmeds['amax_records'], 1)
        self.assertEqual(qmeds['channel_width'], 0.182)
        self.assertEqual(qmeds['area'], 1.172)
        self.assertEqual(round(qmeds['descriptors_1999'], 4), 0.2671)

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
                                            urbext=0)
        self.assertEqual(round(catchment.qmed(), 4), 0.5909)

    def test_best_method_amax(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        self.assertEqual(catchment.qmed(), 1.0)

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
    catchment.descriptors = Descriptors(dtm_area=2.345,
                                        bfihost=0.0,
                                        sprhost=100,
                                        saar=2000,
                                        farl=0.5,
                                        urbext=0,
                                        centroid_ngr=(0, 0))
    # QMED descr rural = 0.6173

    donor_catchment = Catchment("Aberdeen", "River Dee")
    donor_catchment.descriptors = Descriptors(dtm_area=1,
                                              bfihost=0.50,
                                              sprhost=50,
                                              saar=1000,
                                              farl=1,
                                              urbext=1,
                                              centroid_ngr=(0, 0))
    donor_catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                    AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
    # donor QMED descr rural = .5909
    # donor QMED amax = 1.0

    def test_donor_adjustment_factor(self):
        # 1.0/ 0.5909
        self.assertEqual(round(QmedAnalysis(self.catchment)._donor_adj_factor(self.donor_catchment), 4), 1.6925)

    def test_donor_corrected_qmed(self):
        # 0.6173 * 1.6925
        self.assertEqual(
            round(QmedAnalysis(self.catchment).qmed(method='descriptors_2008', donor_catchment=self.donor_catchment),
                  4), 1.0448)