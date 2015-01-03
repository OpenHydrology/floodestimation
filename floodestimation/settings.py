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

import os.path
import configparser
from appdirs import AppDirs


# Some standard names
APP_NAME = 'fehdata'
APP_AUTHOR = 'Open Hydrology'

# Folder to store data
DATA_FOLDER = AppDirs(APP_NAME, APP_AUTHOR).user_data_dir
os.makedirs(DATA_FOLDER, exist_ok=True)

# Cache folder
CACHE_FOLDER = AppDirs(APP_NAME, APP_AUTHOR).user_cache_dir
os.makedirs(CACHE_FOLDER, exist_ok=True)

# Sqlite database for FEH data
DB_FILE_PATH = os.path.join(DATA_FOLDER, 'fehdata.sqlite')


class Config(configparser.ConfigParser):
    """
    Configuration/settings object.

    Settings are read from a `config.ini` file within the python package (default values) or from the user's appdata
    folder. Data is read immediately when object initiated. Data are only written to user file.
    """
    FILE_NAME = 'config.ini'

    def __init__(self):
        configparser.ConfigParser.__init__(self)
        here = os.path.abspath(os.path.dirname(__file__))
        # Read defaults
        self.read_file(open(os.path.join(here, self.FILE_NAME), encoding='utf-8'))
        # Read any user settings
        self.user_config_file = os.path.join(DATA_FOLDER, self.FILE_NAME)
        self.read()

    def read(self):
        """
        Read config data from user config file.
        """
        configparser.ConfigParser.read(self, self.user_config_file, encoding='utf-8')

    def save(self):
        """
        Write data to user config file.
        """
        with open(self.user_config_file, 'w', encoding='utf-8') as f:
            configparser.ConfigParser.write(self, f)

# Create config object immediately when module is imported
config = Config()
