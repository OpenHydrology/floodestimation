from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='floodestimation',
    version='0.1.3',
    packages=['floodestimation'],
    url='https://github.com/OpenHydrology/floodestimation',
    license='GPLv3',
    author='Neil Nutt, Florenz A. P. Hollebrandse',
    author_email='f.a.p.hollebrandse@protonmail.ch',
    description='Library for estimating flood flow rates',
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    install_requires=[
        'numpy',
        'scipy',
        'lmoments3',
        'appdirs',
        'sqlalchemy'
    ],
    package_data={
        'floodestimation': ['fehdata.json'],
    },
)
