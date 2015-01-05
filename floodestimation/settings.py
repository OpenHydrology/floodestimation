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

import os
import configparser
from datetime import datetime
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
        self._default_config_file = os.path.join(here, self.FILE_NAME)
        self._user_config_file = os.path.join(DATA_FOLDER, self.FILE_NAME)
        self.read_defaults()
        self.read()

    def reset(self):
        """
        Restore the default configuration and remove the user's config file.
        """

        # Delete user config file
        try:
            os.remove(self._user_config_file)
        except FileNotFoundError:
            pass

        # Empty and refill the config object
        for section_name in self.sections():
            self.remove_section(section_name)
        self.read_defaults()

    def read_defaults(self):
        # Read defaults
        self.read_file(open(self._default_config_file, encoding='utf-8'))

    def read(self):
        """
        Read config data from user config file.
        """
        configparser.ConfigParser.read(self, self._user_config_file, encoding='utf-8')

    def save(self):
        """
        Write data to user config file.
        """
        with open(self._user_config_file, 'w', encoding='utf-8') as f:
            self.write(f)

    def get_datetime(self, section, option, fallback):
        """
        Return UTC datetime from timestamp in config file.

        :param section: Config section
        :param option: Config option
        :param fallback: Fallback/default value
        :return: Datetime in UTC
        :rtype: :class:`datetime.datetime`
        """
        try:
            s = self[section][option]
            return datetime.utcfromtimestamp(float(s))
        except KeyError:
            return fallback

# Create config object immediately when module is imported
config = Config()
