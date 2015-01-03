import unittest
import os
from urllib.request import pathname2url

import floodestimation.settings as settings
import floodestimation.fehdata as fehdata


class TestDatabase(unittest.TestCase):
    # Tests in this test case must be run in order to test the full sequence of clearing the cache, downloading the
    # data, unzipping the data and counting the number of am and cd3 files.

    def setUp(self):
        settings.config['nrfa']['oh_json_url'] = \
            'file:' + pathname2url(os.path.abspath('./floodestimation/fehdata_test.json'))

    def test_0_download_url_retrieval(self):
        self.assertTrue(fehdata._retrieve_download_url().endswith(r'/floodestimation/tests/data/FEH_data_small.zip'))

    def test_a_clear_cache(self):
        fehdata.clear_cache()
        self.assertFalse(os.listdir(settings.CACHE_FOLDER))

    def test_b_download(self):
        fehdata.download_data()
        self.assertTrue(os.path.isfile(os.path.join(settings.CACHE_FOLDER, fehdata.CACHE_ZIP)))

    def test_c_unzip(self):
        fehdata.unzip_data()
        self.assertTrue(os.path.isdir(os.path.join(settings.CACHE_FOLDER, 'Not suitable for QMED or Pooling')))
        self.assertTrue(os.path.isdir(os.path.join(settings.CACHE_FOLDER, 'Suitable for Pooling')))
        self.assertTrue(os.path.isdir(os.path.join(settings.CACHE_FOLDER, 'Suitable for QMED')))

    def test_d_amax_files(self):
        self.assertEqual(len(fehdata.amax_files()), 6)

    def test_e_cd3_files(self):
        self.assertEqual(len(fehdata.cd3_files()), 6)
