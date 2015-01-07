import unittest
from floodestimation import db
from floodestimation.entities import Catchment


class TestDatabaseCreation(unittest.TestCase):
    all_tables = ['amaxrecords', 'catchments', 'comments', 'descriptors', 'potdatagaps', 'potdatasets', 'potrecords']

    def test_database_contains_all_tables(self):
        self.assertEqual(self.all_tables,
                         sorted(list(db.metadata.tables.keys())))

    def test_open_and_close_session(self):
        db_session = db.Session()
        db_session.close()

    def test_reset_db_tables(self):
        db_session = db.Session()
        db_session.add(Catchment(location="Aberdeen", watercourse="River Dee"))
        db_session.commit()
        db_session.close()

        db.reset_db_tables()

        self.assertEqual(self.all_tables,
                         sorted(list(db.metadata.tables.keys())))
        self.assertEqual(db_session.query(Catchment).count(), 0)

    def test_empty_db_tables(self):
        db_session = db.Session()
        db_session.add(Catchment(location="Aberdeen", watercourse="River Dee"))
        db_session.commit()

        db.empty_db_tables()

        self.assertEqual(self.all_tables,
                         sorted(list(db.metadata.tables.keys())))
        self.assertEqual(db_session.query(Catchment).count(), 0)
        db_session.close()