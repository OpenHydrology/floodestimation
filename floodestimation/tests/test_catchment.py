import unittest
from floodestimation.catchment import Catchment


class TestCatchmentObject(unittest.TestCase):
    def test_catchment_location_watercourse(self):
        catchment = Catchment("Aberdeen", "River Dee")
        self.assertEqual(catchment.location, "Aberdeen")
        self.assertEqual(catchment.watercourse, "River Dee")

    def test_catchment_location_only(self):
        catchment = Catchment("Aberdeen")
        self.assertEqual(catchment.location, "Aberdeen")
        self.assertEqual(catchment.watercourse, "Unknown watercourse")

    def test_catchment_no_location(self):
        with self.assertRaises(TypeError):
            catchment = Catchment()