from setuptools import setup
from os import path
import version

# Update version from GIT tags if possible and create version file
version.update()

here = path.abspath(path.dirname(__file__))
version = open(path.join(here, 'VERSION')).read().split('-')[0]


setup(
    name='floodestimation',
    version=version,
    packages=['floodestimation'],
    package_data={
        'floodestimation': ['fehdata.json',
                            'config.ini'],
    },
)
