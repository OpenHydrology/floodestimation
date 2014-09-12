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

from urllib.request import urlopen, pathname2url
import os
import shutil
import json
from zipfile import ZipFile
from codecs import open
# Current package imports
from . import settings


CACHE_ZIP = 'FEH_data.zip'


def retrieve_download_url():
    """
    Retrieves download location for FEH data zip file from hosted json configuration file.
    :return:
    """
    try:
        # Try to obtain the url from the Open Hydrology json config file.
        with urlopen(settings.OPEN_HYDROLOGY_JSON_URL, timeout=10) as f:
            config = json.loads(f.read().decode('utf-8'))
        # This is just for testing, assuming a relative local file path starting with ./
        if config['feh_data_url'].startswith('.'):
            config['feh_data_url'] = 'file:' + pathname2url(os.path.abspath(config['feh_data_url']))
        return config['feh_data_url']
    except:
        # If that fails (for whatever reason) use the fallback constant.
        return settings.FEH_DATA_URL


def download_data():
    """
    Downloads complete station dataset including catchment descriptors and amax records. And saves it into a cache
    folder.
    """
    with urlopen(retrieve_download_url()) as f:
        with open(os.path.join(settings.CACHE_FOLDER, CACHE_ZIP), "wb") as local_file:
            local_file.write(f.read())


def unzip_data():
    """
    Extract all files from downloaded FEH data zip file.
    """
    with ZipFile(os.path.join(settings.CACHE_FOLDER, CACHE_ZIP), 'r') as zf:
        zf.extractall(path=settings.CACHE_FOLDER)


def clear_cache():
    """
    Delete all files from cache folder.
    """
    shutil.rmtree(settings.CACHE_FOLDER)
    os.makedirs(settings.CACHE_FOLDER)


def amax_files():
    """
    Return all annual maximum flow (*.am) files in cache folder and sub folders.
    :return: List of file paths
    :rtype: list
    """
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(settings.CACHE_FOLDER)
            for f in filenames if os.path.splitext(f)[1].lower() == '.am']


def cd3_files():
    """
    Return all catchment descriptor files (*.cd3) files in cache folder and sub folders.
    :return: List of file paths
    :rtype: list
    """
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(settings.CACHE_FOLDER)
            for f in filenames if os.path.splitext(f)[1].lower() == '.cd3']
