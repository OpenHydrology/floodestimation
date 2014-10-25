import unittest
from floodestimation import db
from floodestimation.entities import Catchment
from sqlalchemy.schema import MetaData
from sqlalchemy.orm.exc import NoResultFound


class TestDatabaseCreation(unittest.TestCase):
    all_tables = ['amaxrecords', 'catchments', 'comments', 'descriptors', 'potdatagaps', 'potdatasets', 'potrecords']

    def test_database_contains_all_tables(self):
        metadata = MetaData(bind=db.engine, reflect=True)
        self.assertEqual(self.all_tables,
                         sorted(list(metadata.tables.keys())))

    def test_open_and_close_session(self):
        db_session = db.Session()
        db_session.close()

    def test_reset_db_tables(self):
        db_session = db.Session()
        db_session.add(Catchment(location="Aberdeen", watercourse="River Dee"))
        db_session.commit()

        db.reset_db_tables()
        metadata = MetaData(bind=db.engine, reflect=True)
        self.assertEqual(self.all_tables,
                         sorted(list(metadata.tables.keys())))
        self.assertEqual(db_session.query(Catchment).count(), 0)

