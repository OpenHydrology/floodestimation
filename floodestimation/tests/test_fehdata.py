import unittest
import floodestimation.fehdata as fehdata
import os


class TestDatabase(unittest.TestCase):
    def test_download(self):
        fehdata.download_data()
        self.assertTrue(os.path.isfile(os.path.join(fehdata.CACHE_FOLDER, fehdata.CACHE_ZIP)))

    def test_unzip(self):
        fehdata.unzip_data()