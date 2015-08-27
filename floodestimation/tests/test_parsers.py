import unittest
from datetime import date
from floodestimation import parsers
from floodestimation.entities import Catchment, Point


class TestAmax(unittest.TestCase):
    parser = parsers.AmaxParser()
    file = 'floodestimation/tests/data/17002.AM'
    amax_records = parser.parse(file)

    def test_amax_parse_length(self):
        self.assertEqual(len(self.amax_records), 4)

    def test_amax_parse_first_item_flow(self):
        self.assertEqual(self.amax_records[0].flow, 34.995)

    def test_amax_parse_first_item_water_year(self):
        self.assertEqual(self.amax_records[0].water_year, 1968)

    def test_amax_parse_second_item_water_year(self):
        self.assertEqual(self.amax_records[1].water_year, 1969)

    def test_amax_parse_valid_record(self):
        self.assertEqual(self.amax_records[0].flag, 0)

    def test_amax_parse_rejected_record(self):
        self.assertEqual(self.parser.rejected_years, [1971, 2002, 2003])
        self.assertEqual(self.amax_records[3].flag, 2)

    def test_amax_without_stage(self):
        amax_records = self.parser.parse('floodestimation/tests/data/17002-nostage.AM')
        self.assertIsNone(amax_records[0].stage)


class TestPot(unittest.TestCase):
    parser = parsers.PotParser()
    file = 'floodestimation/tests/data/17002.PT'
    pot_dataset = parser.parse(file)

    def test_meta_data(self):
        self.assertEqual(self.pot_dataset.catchment_id, 17002)
        self.assertEqual(self.pot_dataset.start_date, date(1968, 12, 21))
        self.assertEqual(self.pot_dataset.end_date, date(2006, 8, 19))
        self.assertAlmostEqual(self.pot_dataset.threshold, 23.809)

    def test_record_count(self):
        self.assertEqual(len(self.pot_dataset.pot_records), 146)

    def test_first_record(self):
        self.assertEqual(self.pot_dataset.pot_records[0].date, date(1969, 1, 12))
        self.assertAlmostEqual(self.pot_dataset.pot_records[0].flow, 34.995)
        self.assertAlmostEqual(self.pot_dataset.pot_records[0].stage, 1.040)

    def test_gaps_count(self):
        self.assertEqual(len(self.pot_dataset.pot_data_gaps), 6)

    def test_first_gap(self):
        self.assertEqual(self.pot_dataset.pot_data_gaps[0].start_date, date(1977, 9, 7))
        self.assertEqual(self.pot_dataset.pot_data_gaps[0].end_date, date(1977, 9, 27))
        self.assertAlmostEqual(self.pot_dataset.pot_data_gaps[0].gap_length(), 21/365)


class TestCd3(unittest.TestCase):
    parser = parsers.Cd3Parser()
    file = 'floodestimation/tests/data/17002.CD3'
    catchment = parser.parse(file)

    def test_object_type(self):
        self.assertTrue(isinstance(self.catchment, Catchment))

    def test_station_number(self):
        self.assertEqual(self.catchment.id, 17002)

    def test_watercourse(self):
        self.assertEqual(self.catchment.watercourse, 'River Leven')

    def test_location(self):
        self.assertEqual(self.catchment.location, 'Leven')

    def test_country(self):
        self.assertEqual(self.catchment.country, 'gb')

    def test_area(self):
        self.assertEqual(self.catchment.area, 424.0)

    def test_coordinate(self):
        self.assertEqual(self.catchment.point, Point(336900, 700600))

    def test_descriptors(self):
        self.assertEqual(self.catchment.descriptors.ihdtm_ngr, Point(336950, 700550))
        self.assertEqual(self.catchment.descriptors.centroid_ngr, Point(317325, 699832))
        self.assertEqual(self.catchment.descriptors.dtm_area, 416.56)
        self.assertEqual(self.catchment.descriptors.altbar, 151)
        self.assertEqual(self.catchment.descriptors.aspbar, 123)
        self.assertEqual(self.catchment.descriptors.aspvar, 0.22)
        self.assertEqual(self.catchment.descriptors.bfihost, 0.511)
        self.assertEqual(self.catchment.descriptors.dplbar, 26.93)
        self.assertEqual(self.catchment.descriptors.dpsbar, 62.9)
        self.assertEqual(self.catchment.descriptors.farl, 0.824)
        self.assertEqual(self.catchment.descriptors.fpext, 0.1009)
        self.assertEqual(self.catchment.descriptors.ldp, 48.74)
        self.assertEqual(self.catchment.descriptors.propwet, 0.45)
        self.assertEqual(self.catchment.descriptors.rmed_1h,  8.8)
        self.assertEqual(self.catchment.descriptors.rmed_1d, 35.5)
        self.assertEqual(self.catchment.descriptors.rmed_2d, 47.1)
        self.assertEqual(self.catchment.descriptors.saar, 947)
        self.assertEqual(self.catchment.descriptors.saar4170, 951)
        self.assertEqual(self.catchment.descriptors.sprhost, 34.62)
        self.assertEqual(self.catchment.descriptors.urbconc1990, None)
        self.assertEqual(self.catchment.descriptors.urbext1990, 0.0173)
        self.assertEqual(self.catchment.descriptors.urbloc1990, None)
        self.assertEqual(self.catchment.descriptors.urbconc2000, 0.830)
        self.assertEqual(self.catchment.descriptors.urbext2000, 0.0361)
        self.assertEqual(self.catchment.descriptors.urbloc2000, 0.702)

    def test_suitability(self):
        self.assertTrue(self.catchment.is_suitable_for_qmed)
        self.assertFalse(self.catchment.is_suitable_for_pooling)

    def test_comments(self):
        comment = [comment.content for comment in self.catchment.comments if comment.title == 'station'][0]
        self.assertEqual(comment,
                         'Velocity-area station on a straight reach of river with artificially heightened and steeped '
                         'banks. The control was formerly a gravel bar, in Sep 1977 stabilised with gabions to form an '
                         'irregular broad-crested weir. Possible movement in control, evident at low flows. Weir is '
                         'thought to be modular throughout range. All flows contained to date. RATING COMMENTS:Rating '
                         'derived from current meter gaugings up to 1.6m (about QMED), simple extrapolation beyond.')

    def test_comment_count(self):
        self.assertEqual(len(self.catchment.comments), 4)


class TestCd3Ireland(unittest.TestCase):
    parser = parsers.Cd3Parser()
    file = 'floodestimation/tests/data/201002.CD3'
    catchment = parser.parse(file)

    def test_country(self):
        self.assertEqual(self.catchment.country, 'ni')

    def test_coordinate(self):
        self.assertEqual(self.catchment.point, Point(240500, 375700))

    def test_descriptors(self):
        self.assertEqual(self.catchment.descriptors.ihdtm_ngr, Point(240500, 375700))
        self.assertEqual(self.catchment.descriptors.centroid_ngr, Point(232140, 375415))


class TestXmlCatchment(unittest.TestCase):
    parser = parsers.XmlCatchmentParser()
    file = 'floodestimation/tests/data/NN 04000 48400.xml'
    catchment = parser.parse(file)

    def test_object_type(self):
        self.assertTrue(isinstance(self.catchment, Catchment))

    def test_station_number(self):
        self.assertEqual(self.catchment.id, None)

    def test_country(self):
        self.assertEqual(self.catchment.country, 'gb')

    def test_area(self):
        self.assertEqual(self.catchment.area, 30.09)

    def test_coordinate(self):
        self.assertEqual(self.catchment.point, Point(204000, 748400))

    def test_descriptors(self):
        self.assertEqual(self.catchment.descriptors.ihdtm_ngr, Point(204000, 748400))
        self.assertEqual(self.catchment.descriptors.centroid_ngr, Point(207378, 751487))
        self.assertEqual(self.catchment.descriptors.dtm_area, 30.09)
        self.assertEqual(self.catchment.descriptors.altbar, 367)
        self.assertEqual(self.catchment.descriptors.aspbar, 247)
        self.assertEqual(self.catchment.descriptors.aspvar, 0.17)
        self.assertEqual(self.catchment.descriptors.bfihost, 0.394)
        self.assertEqual(self.catchment.descriptors.dplbar, 6.56)
        self.assertEqual(self.catchment.descriptors.dpsbar, 356.3)
        self.assertEqual(self.catchment.descriptors.farl, 0.986)
        self.assertEqual(self.catchment.descriptors.fpext, 0.0369)
        self.assertEqual(self.catchment.descriptors.ldp, 11.5)
        self.assertEqual(self.catchment.descriptors.propwet, 0.79)
        self.assertEqual(self.catchment.descriptors.rmed_1h,  13.9)
        self.assertEqual(self.catchment.descriptors.rmed_1d, 72.0)
        self.assertEqual(self.catchment.descriptors.rmed_2d, 112.4)
        self.assertEqual(self.catchment.descriptors.saar, 2810)
        self.assertEqual(self.catchment.descriptors.saar4170, 2969)
        self.assertEqual(self.catchment.descriptors.sprhost, 53.35)
        self.assertEqual(self.catchment.descriptors.urbconc1990, None)
        self.assertEqual(self.catchment.descriptors.urbext1990, 0.0)
        self.assertEqual(self.catchment.descriptors.urbloc1990, None)
        self.assertEqual(self.catchment.descriptors.urbconc2000, None)
        self.assertEqual(self.catchment.descriptors.urbext2000, 0.0)
        self.assertEqual(self.catchment.descriptors.urbloc2000, None)
