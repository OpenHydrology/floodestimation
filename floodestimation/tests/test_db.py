import unittest
from floodestimation import db
from sqlalchemy.schema import MetaData


class TestDatabaseCreation(unittest.TestCase):
    def test_database_contains_all_tables(self):
        metadata = MetaData(bind=db.engine, reflect=True)
        self.assertEqual(['amaxrecords', 'catchments', 'comments', 'descriptors'],
                         sorted(list(metadata.tables.keys())))

    def test_open_and_close_session(self):
        db_session = db.Session()
        db_session.commit()
