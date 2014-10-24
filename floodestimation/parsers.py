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
Parsers for FEH-style data files.

Module contains base parser class and subclassses for parsing CD3 files and AMAX files.

Example:

>>> from floodestimation import parsers
>>> catchment = parsers.Cd3Parser().parse("17002.CD3")
>>> catchment.amax_records = parsers.AmaxParser().parse("17002.AM")
>>> catchment.id
17002
>>> catchment.watercourse
'River Leven'
>>> catchment.descriptors.dtm_area
416.56
>>> catchment.descriptors.centroid_ngr
(317325, 699832)
>>> catchment.amax_records[0].water_year
1968
>>> catchment.amax_records[0].flow
34.995

"""

import time
import datetime
# Current package imports
from . import entities


class FehFileParser(object):
    """
    Generic parser for FEH file format.

    File consists typically of multiple sections as follows::

        [Section Name]
        field, value
        another field, value 1, value 2
        [End]

    """
    #: Class of object to be returned by parser.
    parsed_class = object

    def __init__(self):
        #: Object that will be returned at end of parsing.
        self.object = None

    def parse(self, file_name):
        """
        Parse entire file and return relevant object.

        :param file_name: File path
        :type file_name: str
        :return: Parsed object
        """
        self.object = self.parsed_class()
        with open(file_name, encoding='utf-8') as f:
            in_section = None  # Holds name of FEH file section while traversing through file.
            for line in f:
                if line.lower().startswith('[end]'):
                    # Leave section
                    in_section = None
                elif line.startswith('['):
                    # Enter section, sanitise `[Section Name]` to `section_name`
                    in_section = line.strip().strip('[]').lower().replace(' ', '_')
                elif in_section:
                    try:
                        # Call method `_section_section_name(line)`
                        getattr(self, '_section_' + in_section)(line.strip())
                    except AttributeError:
                        pass  # Skip unsupported section
        return self.object


class AmaxParser(FehFileParser):
    #: Class to be returned by :meth:`parse`. In this case a list of :class:`AmaxRecord` objects.
    parsed_class = list

    def _section_station_number(self, line):
        # Store station number (not used)
        self.station_number = line

    def _section_am_values(self, line):
        # Spit line in columns
        row = [s.strip() for s in line.split(',')]
        # Date in first column
        date = datetime.date(*time.strptime(row[0], "%d %b %Y")[0:3])  # :class:`datetime.date`
        # Flow rate in second column
        flow = float(row[1])
        if flow < 0:
            flow = None
        # Stage in last column
        stage = float(row[2])
        if stage < 0:
            stage = None
        # Create :class:`AmaxRecord` and add to object
        self.object.append(entities.AmaxRecord(date, flow, stage))


class Cd3Parser(FehFileParser):
    #: Class to be returned by :meth:`parse`. In this case :class:`Catchment` objects.
    parsed_class = entities.Catchment

    def _section_station_number(self, line):
        self.object.id = int(line)

    def _section_cds_details(self, line):
        row = [s.strip() for s in line.split(',')]
        if row[0].lower() == 'name':
            self.object.watercourse = row[1]
        elif row[0].lower() == 'location':
            self.object.location = row[1]
        elif row[0].lower() == 'nominal area':
            self.object.area = float(row[1])
        elif row[0].lower() == 'nominal ngr':
            # (E, N) in meters.
            self.object.point = entities.Point(100*int(row[1]), 100*int(row[2]))

    def _section_descriptors(self, line):
        row = [s.strip() for s in line.split(',')]
        # Make descriptor name a valid python variable, by lowercasing, replacing spaces and hypens with underscore,
        # e.g. `CENTROID NGR` -> `centroid_ngr`
        #      `RMED-1H`      -> `rmed_1h`
        name = row[0].lower().replace(' ', '_').replace('-', '_')

        # Standard numeric descriptors
        if name not in ['ihdtm_ngr', 'centroid_ngr']:
            value = float(row[1])
            # Filter out null-values
            if value == -9.999:
                value = None
            setattr(self.object.descriptors, name, value)

        # Coordinates
        else:
            # (E, N) in meters.
            setattr(self.object.descriptors, name, entities.Point(int(row[2]), int(row[3])))
            # Set country using info provided as part of coordinates.
            country_mapping = {'gb': 'gb',
                               'ireland': 'ni'}
            self.object.country = country_mapping[row[1].lower()]

    def _section_suitability(self, line):
        row = [s.strip().lower() for s in line.split(',')]
        bool_mapping = {'yes': True, 'no': False}
        # E.g. object.is_suitable_for_qmed = True
        setattr(self.object, 'is_suitable_for_' + row[0], bool_mapping[row[1]])

    def _section_comments(self, line):
        row = [s.strip() for s in line.split(',', 1)]
        # E.g. object.comments = [Comment("station", "Velocity-area station on a straight reach ...")]
        self.object.comments.append(entities.Comment(row[0].lower(), row[1]))
