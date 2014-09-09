import unittest
import os
from errno import ENOENT

import floodestimation.settings as settings
from floodestimation.db import Base, engine


class TestDatabaseCreation(unittest.TestCase):
    def setUp(self):
        try:
            os.remove(settings.DB_FILE_PATH)
        except OSError as e:
            if not e.errno == ENOENT:  # File does not exist
                raise

    def tearDown(self):
        try:
            os.remove(settings.DB_FILE_PATH)
        except OSError as e:
            if not e.errno == ENOENT:  # File does not exist
                raise

    def test_create_new_db_on_import(self):
        self.assertEqual(['amaxrecords', 'catchments', 'comments', 'descriptors'],
                         sorted(list(Base.metadata.tables.keys())))
