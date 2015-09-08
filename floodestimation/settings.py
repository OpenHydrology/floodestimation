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


class Config(configparser.ConfigParser):
    """
    Configuration/settings object.

    Settings are read from a `config.ini` file within the python package (default values) or from the user's appdata
    folder. Data is read immediately when object initiated. Data are only written to user file.
    """
    FILE_NAME = 'config.ini'
    APP_NAME = 'fehdata'
    APP_ORG = 'Open Hydrology'

    def __init__(self):
        configparser.ConfigParser.__init__(self)

        here = os.path.abspath(os.path.dirname(__file__))
        self._app_folders = AppDirs(self.APP_NAME, self.APP_ORG)
        self._default_config_file = os.path.join(here, self.FILE_NAME)

        os.makedirs(self._app_folders.user_config_dir, exist_ok=True)  # Create folder in advance if necessary
        self._user_config_file = os.path.join(self._app_folders.user_config_dir, self.FILE_NAME)

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
        # Setup standard folders
        data_folder = self._app_folders.user_data_dir
        os.makedirs(data_folder, exist_ok=True)
        cache_folder = self._app_folders.user_cache_dir
        os.makedirs(cache_folder, exist_ok=True)

        # Make them available in the defaults section
        self['DEFAULT'] = {
            'data_folder': data_folder,
            'cache_folder': cache_folder
        }

        # Read any other default sections and options from the package's config file
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
        except (KeyError, ValueError):
            return fallback

    def set_datetime(self, section, option, value):
        """
        Return UTC datetime from timestamp in config file.

        :param section: Config section
        :param option: Config option
        :param value: Datetime value to set
        :type value: :class:`datetime.datetime`
        """
        self[section][option] = str(value.timestamp())

# Create config object immediately when module is imported
config = Config()
