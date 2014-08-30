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

    def test_catchment_distance(self):
        catchment_1 = Catchment("Aberdeen", "River Dee")
        catchment_1.descriptors['centroid'] = (0, 0)

        catchment_2 = Catchment("Dundee", "River Tay")
        catchment_2.descriptors['centroid'] = (3, 4)

        self.assertEqual(catchment_1.distance_to(catchment_2), 5)