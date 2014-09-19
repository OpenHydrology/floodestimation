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
This module contains some convenience functions for quickly loading catchments (incl. annual maximum flow data) from
CD3-files and to download all gauged catchments and save into a sqlite database.
"""

import os.path as path
# Current package imports
from . import fehdata
from . import parsers


def load_catchment(cd3_file_path):
    """
    Load catchment object from a CD3 file. This assumes there is also a corresponding AM file in the same folder as the
    CD3 file.

    :param cd3_file_path: File location of CD3 file
    :type cd3_file_path: str
    :return: Catchment object including the `amax_records` attribute.
    :rtype: :class:`floodestimation.entities.Catchment`
    """
    am_file_path = path.splitext(cd3_file_path)[0] + '.AM'

    catchment = parsers.Cd3Parser().parse(cd3_file_path)
    try:
        catchment.amax_records = parsers.AmaxParser().parse(am_file_path)
    except FileNotFoundError:
        catchment.amax_records = []

    return catchment


def gauged_catchments_to_db(session):
    """
    Retrieves all gauged catchments (incl. catchment descriptors and annual maximum flow data) from the National River
    Flow Archive and saves it to a (sqlite) database.

    :param session: database session to use, typically :meth:`floodestimation.db.Session()`
    :type session: `sqlalchemy.orm.session.Session`
    """
    fehdata.clear_cache()
    fehdata.download_data()
    fehdata.unzip_data()

    for cd3_file_path in fehdata.cd3_files():
        catchment = load_catchment(cd3_file_path)
        session.add(catchment)