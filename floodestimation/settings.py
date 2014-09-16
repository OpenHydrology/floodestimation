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

import os
from appdirs import AppDirs

# Some standard names
APP_NAME = 'fehdata'
APP_AUTHOR = 'Open Hydrology'

# URL to retrieve json file with settings, e.g. FEH data download locations
OPEN_HYDROLOGY_JSON_URL = \
    'https://github.com/OpenHydrology/StatisticalFloodEstimationTool/blob/master/floodestimation/fehdata.json'
# Default FEH data download location
FEH_DATA_URL = 'http://www.ceh.ac.uk/data/nrfa/peak_flow/WINFAP-FEH_v3.3.4.zip'

# Folder to store data
DATA_FOLDER = AppDirs(APP_NAME, APP_AUTHOR).user_data_dir
os.makedirs(DATA_FOLDER, exist_ok=True)

# Cache folder
CACHE_FOLDER = AppDirs(APP_NAME, APP_AUTHOR).user_cache_dir
os.makedirs(CACHE_FOLDER, exist_ok=True)

# Sqlite database for FEH data
DB_FILE_PATH = os.path.join(DATA_FOLDER, 'fehdata.sqlite')