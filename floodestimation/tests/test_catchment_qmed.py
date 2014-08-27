import unittest
from datetime import date
from floodestimation.catchment import Catchment, AmaxRecord


class TestCatchmentQmed(unittest.TestCase):
    def test_channel_width_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        self.assertEqual(catchment.qmed_from_channel_width(), 0.182)

    def test_channel_width_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 2.345
        self.assertEqual(round(catchment.qmed_from_channel_width(), 4), 0.9839)

    def test_channel_width_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 50
        self.assertEqual(round(catchment.qmed_from_channel_width(), 4), 420.7576)

    def test_channel_no_width(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            catchment.qmed_from_channel_width()
        except Exception as e:
            self.assertEqual(str(e), "Catchment `channel_width` attribute must be set first.")

    def test_area_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors['area'] = 1
        self.assertEqual(catchment.qmed_from_area(), 1.172)

    def test_area_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors['area'] = 2.345
        self.assertEqual(round(catchment.qmed_from_area(), 4), 2.6946)

    def test_area_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors['area'] = 100
        self.assertEqual(round(catchment.qmed_from_area(), 4), 81.2790)

    def test_no_area(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            catchment.qmed_from_area()
        except Exception as e:
            self.assertEqual(str(e), "Catchment `descriptors` attribute must be set first.")

    def test_descriptors_1999_1(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = {'area': 1,
                                 'bfihost': 0.50,
                                 'sprhost': 50,
                                 'saar': 1000,
                                 'farl': 1}
        self.assertEqual(round(catchment.qmed_from_descriptors_1999(), 4), 0.2671)

    def test_descriptors_1999_2(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = {'area': 2.345,
                                 'bfihost': 0,
                                 'sprhost': 100,
                                 'saar': 2000,
                                 'farl': 0.5}
        self.assertEqual(round(catchment.qmed_from_descriptors_1999(), 4), 0.3729)

    def test_descriptors_1999_3(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors = {'area': 100,
                                 'bfihost': 0.50,
                                 'sprhost': 50,
                                 'saar': 1000,
                                 'farl': 1}
        self.assertEqual(round(catchment.qmed_from_descriptors_1999(), 4), 18.5262)

    def test_no_descriptors_1999(self):
        catchment = Catchment("Aberdeen", "River Dee")
        try:
            catchment.qmed_from_descriptors_1999()
        except Exception as e:
            self.assertEqual(str(e), "Catchment `descriptors` attribute must be set first.")

    def test_all(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 1.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 1.0, 0.5)]
        catchment.descriptors = {'area': 1,
                                 'bfihost': 0.50,
                                 'sprhost': 50,
                                 'saar': 1000,
                                 'farl': 1}
        qmeds = catchment.qmed_all_methods()
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
        catchment.descriptors['area'] = 1
        self.assertEqual(catchment.qmed(), 1.172)

    def test_best_method_descriptors(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.channel_width = 1
        catchment.descriptors = {'area': 1,
                                 'bfihost': 0.50,
                                 'sprhost': 50,
                                 'saar': 1000,
                                 'farl': 1}
        self.assertEqual(round(catchment.qmed(), 4), 0.2671)

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
        catchment.descriptors = {'area': 1,
                                 'bfihost': 0.50,
                                 'sprhost': 50,
                                 'saar': 1000,
                                 'farl': 1}
        self.assertEqual(catchment.qmed(), 1.0)
