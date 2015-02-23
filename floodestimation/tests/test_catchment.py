import unittest
from datetime import date
from floodestimation import db
from floodestimation.entities import Catchment, AmaxRecord, Point, PotRecord, PotDataGap, PotDataset, PotPeriod


class TestCatchmentObject(unittest.TestCase):
    def test_catchment_location_watercourse(self):
        catchment = Catchment("Aberdeen", "River Dee")
        self.assertEqual(catchment.location, "Aberdeen")
        self.assertEqual(catchment.watercourse, "River Dee")

    def test_catchment_location_only(self):
        catchment = Catchment("Aberdeen")
        self.assertEqual(catchment.location, "Aberdeen")
        self.assertEqual(catchment.watercourse, None)

    def test_catchment_distance_no_country(self):
        catchment_1 = Catchment("Aberdeen", "River Dee")
        catchment_1.descriptors.centroid_ngr = Point(0, 0)

        catchment_2 = Catchment("Dundee", "River Tay")
        catchment_2.descriptors.centroid_ngr = Point(3000, 4000)

        self.assertEqual(catchment_1.distance_to(catchment_2), 5)

    def test_catchment_distance_same_country(self):
        catchment_1 = Catchment("Aberdeen", "River Dee")
        catchment_1.descriptors.centroid_ngr = Point(0, 0)
        catchment_1.country = 'gb'

        catchment_2 = Catchment("Dundee", "River Tay")
        catchment_2.descriptors.centroid_ngr = Point(3000, 4000)
        catchment_2.country = 'gb'

        self.assertEqual(catchment_1.distance_to(catchment_2), 5)

    def test_catchment_distance_different_country(self):
        catchment_1 = Catchment("Aberdeen", "River Dee")
        catchment_1.descriptors.centroid_ngr = Point(0, 0)

        catchment_2 = Catchment("Belfast")
        catchment_2.descriptors.centroid_ngr = Point(3, 4)
        catchment_2.country = 'ni'

        self.assertEqual(catchment_1.distance_to(catchment_2), float('inf'))

    def test_urbext_2000(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.urbext2000 = 1.2345
        self.assertGreaterEqual(catchment.descriptors.urbext(2000), 1.2345)

    def test_urbext_2015(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.urbext2000 = 1.2345
        self.assertAlmostEqual(catchment.descriptors.urbext(2015), 1.2750335)

    def test_urbext_today(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.descriptors.urbext2000 = 1.2345
        self.assertGreaterEqual(catchment.descriptors.urbext(date.today().year), 1.275033)

    def test_record_start_end(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 3.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2001, 12, 31), 1.0, 0.5)]
        self.assertEqual(catchment.amax_records_start(), 1999)
        self.assertEqual(catchment.amax_records_end(), 2001)


class TestCatchmentPotRecords(unittest.TestCase):
    def test_pot_record(self):
        record = PotRecord(date(2000, 12, 31), 1.0, 0.5)
        self.assertEqual(record.date.year, 2000)
        self.assertEqual(record.date.month, 12)
        self.assertEqual(record.date.day, 31)
        self.assertAlmostEqual(record.flow, 1.0)
        self.assertAlmostEqual(record.stage, 0.5)

    def test_data_gap_length(self):
        pot_data_gap = PotDataGap(start_date=date(2000, 12, 1), end_date=date(2000, 12, 31))
        self.assertAlmostEqual(pot_data_gap.gap_length(), 0.0849315)

    def test_pot_dataset_record_length(self):
        pot_dataset = PotDataset(start_date=date(2000, 12, 31), end_date=date(2001, 12, 30))
        self.assertAlmostEqual(pot_dataset.record_length(), 1)

    def test_pot_dataset_record_length_with_gap(self):
        pot_dataset = PotDataset(start_date=date(2000, 12, 31), end_date=date(2001, 12, 30))
        pot_data_gap = PotDataGap(start_date=date(2001, 1, 1), end_date=date(2001, 1, 31))
        pot_dataset.pot_data_gaps.append(pot_data_gap)
        self.assertAlmostEqual(pot_dataset.record_length(), 0.9150685)

    def test_pot_periods(self):
        pot_dataset = PotDataset(start_date=date(2000, 12, 31), end_date=date(2001, 12, 30))
        pot_data_gap = PotDataGap(start_date=date(2001, 1, 1), end_date=date(2001, 1, 31))
        pot_dataset.pot_data_gaps.append(pot_data_gap)

        self.assertEqual(pot_dataset.continuous_periods(), [
            PotPeriod(date(2000, 12, 31), date(2000, 12, 31)),
            PotPeriod(date(2001, 2, 1), date(2001, 12, 30))
        ])
        self.assertAlmostEqual(sum(period.period_length() for period in pot_dataset.continuous_periods()), 0.9150685)

    def test_pot_periods_no_gaps(self):
        pot_dataset = PotDataset(start_date=date(2000, 12, 31), end_date=date(2001, 12, 30))

        self.assertEqual(pot_dataset.continuous_periods(), [
            PotPeriod(date(2000, 12, 31), date(2001, 12, 30))
        ])


class TestCatchmentDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_session = db.Session()

    def tearDown(self):
        self.db_session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.db_session.close()

    def test_add_catchment(self):
        catchment = Catchment(location="Aberdeen", watercourse="River Dee")
        self.db_session.add(catchment)
        result = self.db_session.query(Catchment).filter_by(location="Aberdeen", watercourse="River Dee").one()
        self.assertIs(catchment, result)

    def test_add_catchment_with_amax(self):
        catchment = Catchment("Aberdeen", "River Dee")
        catchment.amax_records = [AmaxRecord(date(1999, 12, 31), 3.0, 0.5),
                                  AmaxRecord(date(2000, 12, 31), 2.0, 0.5),
                                  AmaxRecord(date(2001, 12, 31), 1.0, 0.5)]
        self.db_session.add(catchment)
        result = self.db_session.query(Catchment).filter_by(location="Aberdeen", watercourse="River Dee").one()
        self.assertEqual(catchment, result)
        self.assertEqual(catchment.amax_records, result.amax_records)
