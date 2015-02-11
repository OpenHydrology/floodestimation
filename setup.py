from setuptools import setup


setup(
    name='floodestimation',
    version='0.3.0',
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
