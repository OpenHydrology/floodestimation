import unittest
import floodestimation.fehdata as fehdata
import os


class TestDatabase(unittest.TestCase):
    #@unittest.skip
    def test_a_clear_cache(self):
        fehdata.clear_cache()
        self.assertFalse(os.listdir(fehdata.CACHE_FOLDER))

    #@unittest.skip
    def test_b_download(self):
        fehdata.download_data()
        self.assertTrue(os.path.isfile(os.path.join(fehdata.CACHE_FOLDER, fehdata.CACHE_ZIP)))

    #@unittest.skip
    def test_c_unzip(self):
        fehdata.unzip_data()
        self.assertTrue(os.path.isdir(os.path.join(fehdata.CACHE_FOLDER, 'Not suitable for QMED or Pooling')))
        self.assertTrue(os.path.isdir(os.path.join(fehdata.CACHE_FOLDER, 'Suitable for Pooling')))
        self.assertTrue(os.path.isdir(os.path.join(fehdata.CACHE_FOLDER, 'Suitable for QMED')))

    def test_d_amax_files(self):
        self.assertTrue(len(fehdata.amax_files()), 963)

    def test_e_cd3_files(self):
        self.assertTrue(len(fehdata.cd3_files()), 963)