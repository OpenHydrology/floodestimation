import unittest
from floodestimation import settings


class TestSettings(unittest.TestCase):
    config = settings.config

    def tearDown(self):
        self.config.reset()  # remove the user's config file after each test

    def test_default_config(self):
        self.assertTrue('nrfa' in self.config)
        self.assertTrue('oh_json_url' in self.config['nrfa'])

    def test_user_config(self):
        self.config['nrfa']['test'] = 'test'
        self.config.save()
        self.config = None
        self.config = settings.config
        self.assertTrue(self.config['nrfa']['test'], 'test')

    def test_config_reset(self):
        self.config['nrfa']['test'] = 'test'
        self.config.save()
        self.config.reset()
        self.assertNotIn('test', self.config['nrfa'])
