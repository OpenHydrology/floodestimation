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

import os.path as path
# Current package imports
from . import fehdata
from . import parsers
from . import db


def load_catchment(cd3_file_path):
    am_file_path = path.splitext(cd3_file_path)[0] + '.AM'

    catchment = parsers.Cd3Parser().parse(cd3_file_path)
    catchment.amax_records = parsers.AmaxParser().parse(am_file_path)

    return catchment


def save_catchments_to_db(session):
    fehdata.clear_cache()
    fehdata.download_data()
    fehdata.unzip_data()

    for cd3_file_path in fehdata.cd3_files():
        catchment = load_catchment(cd3_file_path)
        session.add(catchment)