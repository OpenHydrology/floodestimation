# -*- coding: utf-8 -*-

# Copyright (c) 2014  Florenz A.P. Hollebrandse <f.a.p.hollebrandse@protonmail.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides methods to download a complete set of published gauged catchment data from the `National River Flow
Archive <http://www.ceh.ac.uk/data/nrfa/peakflow_overview.html>`_.

Downloaded data files are stored in a Cache folder under the user's application data folder. On Windows, this is folder
is located at `C:\\\\Users\\\\{Username}\\\\AppData\\\\Local\\\\Open Hydrology\\\\fehdata\\\\Cache`.

A typical data retrieval is as follows:

>>> from floodestimation import fehdata
>>> fehdata.clear_cache()
>>> fehdata.download_data()
>>> fehdata.unzip_data()

Data files can then be accessed as follows:

>>> cd3_files = fehdata.cd3_files()
>>> amax_files = fehdata.amax_files()

For parsing CD3 files and AMAX files see :mod:`floodestimation.parsers`.

"""


from urllib.request import urlopen, pathname2url
from urllib.error import URLError
from datetime import datetime, timedelta
import os
import shutil
import json
from zipfile import ZipFile
from distutils.version import LooseVersion
# Current package imports
from .settings import config


CACHE_FOLDER = config['DEFAULT']['cache_folder']
CACHE_ZIP = 'nrfa_data.zip'


def _retrieve_download_url():
    """
    Retrieves download location for FEH data zip file from hosted json configuration file.

    :return: URL for FEH data file
    :rtype: str
    """
    try:
        # Try to obtain the url from the Open Hydrology json config file.
        with urlopen(config['nrfa']['oh_json_url'], timeout=10) as f:
            remote_config = json.loads(f.read().decode('utf-8'))
        # This is just for testing, assuming a relative local file path starting with ./
        if remote_config['nrfa_url'].startswith('.'):
            remote_config['nrfa_url'] = 'file:' + pathname2url(os.path.abspath(remote_config['nrfa_url']))

        # Save retrieved config data
        _update_nrfa_metadata(remote_config)

        return remote_config['nrfa_url']
    except URLError:
        # If that fails (for whatever reason) use the fallback constant.
        return config['nrfa']['url']


def update_available(after_days=1):
    """
    Check whether updated NRFA data is available.

    :param after_days: Only check if not checked previously since a certain number of days ago
    :type after_days: float
    :return: `True` if update available, `False` if not, `None` if remote location cannot be reached.
    :rtype: bool or None
    """
    never_downloaded = not bool(config.get('nrfa', 'downloaded_on', fallback=None) or None)
    if never_downloaded:
        config.set_datetime('nrfa', 'update_checked_on', datetime.utcnow())
        config.save()
        return True

    last_checked_on = config.get_datetime('nrfa', 'update_checked_on', fallback=None) or datetime.fromtimestamp(0)
    if datetime.utcnow() < last_checked_on + timedelta(days=after_days):
        return False

    current_version = LooseVersion(config.get('nrfa', 'version', fallback='0') or '0')
    try:
        with urlopen(config['nrfa']['oh_json_url'], timeout=10) as f:
            remote_version = LooseVersion(json.loads(f.read().decode('utf-8'))['nrfa_version'])
        config.set_datetime('nrfa', 'update_checked_on', datetime.utcnow())
        config.save()
        return remote_version > current_version
    except URLError:
        return None


def download_data():
    """
    Downloads complete station dataset including catchment descriptors and amax records. And saves it into a cache
    folder.
    """
    with urlopen(_retrieve_download_url()) as f:
        with open(os.path.join(CACHE_FOLDER, CACHE_ZIP), "wb") as local_file:
            local_file.write(f.read())


def _update_nrfa_metadata(remote_config):
    """
    Save NRFA metadata to local config file using retrieved config data

    :param remote_config: Downloaded JSON data, not a ConfigParser object!
    """
    config['nrfa']['oh_json_url'] = remote_config['nrfa_oh_json_url']
    config['nrfa']['version'] = remote_config['nrfa_version']
    config['nrfa']['url'] = remote_config['nrfa_url']
    config.set_datetime('nrfa', 'published_on', datetime.utcfromtimestamp(remote_config['nrfa_published_on']))
    config.set_datetime('nrfa', 'downloaded_on', datetime.utcnow())
    config.set_datetime('nrfa', 'update_checked_on', datetime.utcnow())
    config.save()


def nrfa_metadata():
    """
    Return metadata on the NRFA data.

    Returned metadata is a dict with the following elements:

    - `url`: string with NRFA data download URL
    - `version`: string with NRFA version number, e.g. '3.3.4'
    - `published_on`: datetime of data release/publication (only month and year are accurate, rest should be ignored)
    - `downloaded_on`: datetime of last download

    :return: metadata
    :rtype: dict
    """
    result = {
        'url': config.get('nrfa', 'url', fallback=None) or None,  # Empty strings '' become None
        'version': config.get('nrfa', 'version', fallback=None) or None,
        'published_on': config.get_datetime('nrfa', 'published_on', fallback=None) or None,
        'downloaded_on': config.get_datetime('nrfa', 'downloaded_on', fallback=None) or None
    }
    return result


def unzip_data():
    """
    Extract all files from downloaded FEH data zip file.
    """
    with ZipFile(os.path.join(CACHE_FOLDER, CACHE_ZIP), 'r') as zf:
        zf.extractall(path=CACHE_FOLDER)


def clear_cache():
    """
    Delete all files from cache folder.
    """
    shutil.rmtree(CACHE_FOLDER)
    os.makedirs(CACHE_FOLDER)


def amax_files():
    """
    Return all annual maximum flow (`*.am`) files in cache folder and sub folders.

    :return: List of file paths
    :rtype: list
    """
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(CACHE_FOLDER)
            for f in filenames if os.path.splitext(f)[1].lower() == '.am']


def cd3_files():
    """
    Return all catchment descriptor files (`*.cd3`) files in cache folder and sub folders.

    :return: List of file paths
    :rtype: list
    """
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(CACHE_FOLDER)
            for f in filenames if os.path.splitext(f)[1].lower() == '.cd3']
