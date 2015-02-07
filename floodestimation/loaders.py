# -*- coding: utf-8 -*-

# Copyright (c) 2014-2015  Florenz A.P. Hollebrandse <f.a.p.hollebrandse@protonmail.ch>
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
This module contains some convenience functions for quickly loading catchments (incl. annual maximum flow data) from
CD3-files and to download all gauged catchments and save into a sqlite database.
"""

import os.path
# Current package imports
from . import fehdata
from . import parsers
from .settings import config


def from_file(cd3_file_path):
    """
    Load catchment object from a `.CD3` file.

    If there is also a corresponding `.AM` file (annual maximum flow data) or
    a `.PT` file (peaks over threshold data) in the same folder as the CD3 file, these datasets will also be loaded.

    :param cd3_file_path: File location of CD3 file
    :type cd3_file_path: str
    :return: Catchment object with the `amax_records` and `pot_dataset` attributes set (if data available).
    :rtype: :class:`.entities.Catchment`
    """
    am_file_path = os.path.splitext(cd3_file_path)[0] + '.AM'
    pot_file_path = os.path.splitext(cd3_file_path)[0] + '.PT'

    catchment = parsers.Cd3Parser().parse(cd3_file_path)

    # AMAX records
    try:
        catchment.amax_records = parsers.AmaxParser().parse(am_file_path)
    except FileNotFoundError:
        catchment.amax_records = []

    # POT records
    try:
        catchment.pot_dataset = parsers.PotParser().parse(pot_file_path)
    except FileNotFoundError:
        pass

    return catchment


def to_db(catchment, session, method='create', autocommit=False):
    """
    Load catchment object into the database.

    A catchment/station number (:attr:`catchment.id`) must be provided. If :attr:`method` is set to `update`, any
    existing catchment in the database with the same catchment number will be updated.

    :param catchment: New catchment object to replace any existing catchment in the database
    :type catchment: :class:`.entities.Catchment`
    :param session: Database session to use, typically `floodestimation.db.Session()`
    :type session: :class:`sqlalchemy.orm.session.Session`
    :param method: - `create`: only new catchments will be loaded, it must not already exist in the database.
                   - `update`: any existing catchment in the database will be updated. Otherwise it will be created.
    :type method: str
    :param autocommit: Whether to commit the database session immediately. Default: `False`.
    :type autocommit: bool
    """

    if not catchment.id:
        raise ValueError("Catchment/station number (`catchment.id`) must be set.")
    if method == 'create':
        session.add(catchment)
    elif method == 'update':
        session.merge(catchment)
    else:
        raise ValueError("Method `{}` invalid. Use either `create` or `update`.")
    if autocommit:
        session.commit()


def folder_to_db(path, session, method='create', autocommit=False):
    """
    Import an entire folder (incl. sub-folders) into the database

    :param path: Folder location
    :type path: str
    :param session: database session to use, typically `floodestimation.db.Session()`
    :type session: :class:`sqlalchemy.orm.session.Session`
    :param method: - `create`: only new catchments will be loaded, it must not already exist in the database.
                   - `update`: any existing catchment in the database will be updated. Otherwise it will be created.
    :type method: str
    :param autocommit: Whether to commit the database session immediately. Default: `False`.
    :type autocommit: bool
    """
    if not os.path.isdir(path):
        raise ValueError("Folder `{}` does not exist or is not accesible.".format(path))

    cd3_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path)
                 for f in filenames if os.path.splitext(f)[1].lower() == '.cd3']
    for cd3_file_path in cd3_files:
        catchment = from_file(cd3_file_path)
        to_db(catchment, session, method)
    if autocommit:
        session.commit()


# Some specific import methods below:

def nrfa_to_db(session, method='create', autocommit=False):
    """
    Retrieves all gauged catchments (incl. catchment descriptors and annual maximum flow data) from the National River
    Flow Archive and saves it to a (sqlite) database.

    :param session: database session to use, typically `floodestimation.db.Session()`
    :type session: :class:`sqlalchemy.orm.session.Session`
    :param method: - `create`: only new catchments will be loaded, it must not already exist in the database.
                   - `update`: any existing catchment in the database will be updated. Otherwise it will be created.
    :type method: str
    :param autocommit: Whether to commit the database session immediately. Default: `False`.
    :type autocommit: bool
    """

    fehdata.clear_cache()
    fehdata.download_data()
    fehdata.unzip_data()
    folder_to_db(fehdata.CACHE_FOLDER, session, method=method, autocommit=autocommit)


def userdata_to_db(session, method='update', autocommit=False):
    """
    Add catchments from a user folder to the database.

    :param session: database session to use, typically `floodestimation.db.Session()`
    :type session: :class:`sqlalchemy.orm.session.Session`
    :param method: - `create`: only new catchments will be loaded, it must not already exist in the database.
                   - `update`: any existing catchment in the database will be updated. Otherwise it will be created.
    :type method: str
    :param autocommit: Whether to commit the database session immediately. Default: `False`.
    :type autocommit: bool
    """

    try:
        folder = config['import']['folder']
    except KeyError:
        return
    folder_to_db(folder, session, method=method, autocommit=autocommit)
