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
    install_requires=[
        'appdirs>=1.4,<1.5',
        'sqlalchemy>=0.9,<0.10',
        'numpy>=1.9,<1.10',
        'scipy>=0.14',
        'lmoments3>=1.0.2,<1.1'
    ],
    package_data={
        'floodestimation': ['fehdata.json',
                            'config.ini'],
    },
)
