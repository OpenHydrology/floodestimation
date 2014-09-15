import unittest
from floodestimation import db
from floodestimation import loaders
from floodestimation.entities import Catchment


class TestLoaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        cls.session = db.Session()

    def test_load_catchment(self):
        catchment = loaders.load_catchment('floodestimation/tests/data/17002.CD3')
        self.assertEqual(17002, catchment.id)
        self.assertEqual(3, len(catchment.amax_records))

    def test_save_catchments_to_db(self):
        loaders.save_catchments_to_db(self.session)
        expected = ['Ardlethen', "Curry's Bridge", 'Dudgeon Bridge', 'Headswood', 'Inverugie', 'Leven']
        result = [location for (location, ) in self.session.query(Catchment.location).order_by(Catchment.location)]
        self.assertEqual(expected, result)
        self.session.rollback()

