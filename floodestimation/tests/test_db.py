import unittest
import os

import floodestimation.settings as settings
from floodestimation.db import Base, engine


class TestDatabaseCreation(unittest.TestCase):
    def setUp(self):
        try:
            os.remove(settings.DB_FILE_PATH)
        except FileNotFoundError:
            pass

    def tearDown(self):
        try:
            os.remove(settings.DB_FILE_PATH)
        except FileNotFoundError:
            pass

    def test_create_new_db_on_import(self):
        self.assertEqual(['amaxrecords', 'catchments', 'comments', 'descriptors'],
                         sorted(list(Base.metadata.tables.keys())))
