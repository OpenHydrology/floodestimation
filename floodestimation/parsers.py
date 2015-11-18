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
Parsers for FEH-style data files.

Module contains base parser class and subclassses for parsing CD3 files, AMAX files, etc.

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
import xml.etree.ElementTree as ET
import math
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

    def parse_str(self, s):
        """
        Parse string and return relevant object

        :param s: string to parse
        :type s: str
        :return: Parsed object
        """
        self.object = self.parsed_class()
        in_section = None  # Holds name of FEH file section while traversing through file.
        for line in s.split('\n'):
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

    def parse(self, file_name):
        """
        Parse entire file and return relevant object.

        :param file_name: File path
        :type file_name: str
        :return: Parsed object
        """
        self.object = self.parsed_class()
        with open(file_name, encoding='utf-8') as f:
            self.parse_str(f.read())
        return self.object

    @staticmethod
    def parse_feh_date_format(s):
        """
        Return a date object from a string in FEH date format, e.g. `01 Jan 1970`

        :param s: Formatted date string
        :type s: str
        :return: date object
        :rtype: :class:`datetime.date`
        """
        return datetime.date(*time.strptime(s, "%d %b %Y")[0:3])


class AmaxParser(FehFileParser):
    #: Class to be returned by :meth:`parse`. In this case a list of :class:`AmaxRecord` objects.
    parsed_class = list

    def __init__(self):
        super().__init__()
        self.rejected_years = []

    def _section_station_number(self, line):
        # Store station number (not used)
        self.station_number = line

    def _section_am_values(self, line):
        # Spit line in columns
        row = [s.strip() for s in line.split(',')]
        # Date in first column
        date = self.parse_feh_date_format(row[0])

        # Flow rate in second column
        flow = float(row[1])
        flag = 0
        if flow < 0:
            flow = None
            flag = 1  # Invalid value

        # Create instance of :class:`AmaxRecord`
        record = entities.AmaxRecord(date, flow)

        # Stage in third column (may not exist)
        if len(row) >= 3:
            stage = float(row[2])
            if stage < 0:
                stage = None
            record.stage = stage

        # Set flag if the water year is included in the list of rejected years
        if record.water_year in self.rejected_years:
            flag = 2  # Rejected
        record.flag = flag

        self.object.append(record)

    def _section_am_rejected(self, line):
        row = [int(s.strip()) for s in line.split(',')]
        self.rejected_years += list(range(row[0], row[1] + 1))  # Add 1 because AM file interval includes end year


class PotParser(FehFileParser):
    #: Class to be returned by :meth:`parse`. In this case a :class:`PotDataset` objects.
    parsed_class = entities.PotDataset

    def _section_station_number(self, line):
        self.object.catchment_id = int(line.strip())
        self.object.pot_records = []

    def _section_pot_details(self, line):
        row = [s.strip().lower() for s in line.split(',')]
        if row[0] == 'record period':
            self.object.start_date = self.parse_feh_date_format(row[1])
            self.object.end_date = self.parse_feh_date_format(row[2])
        elif row[0] == 'threshold':
            self.object.threshold = float(row[1])

    def _section_pot_gaps(self, line):
        row = [s.strip() for s in line.split(',')]
        pot_data_gap = entities.PotDataGap()
        pot_data_gap.start_date = self.parse_feh_date_format(row[0])
        pot_data_gap.end_date = self.parse_feh_date_format(row[1])
        self.object.pot_data_gaps.append(pot_data_gap)

    def _section_pot_values(self, line):
        row = [s.strip() for s in line.split(',')]
        date = self.parse_feh_date_format(row[0])
        flow = float(row[1])
        if flow < 0:
            flow = None
        try:
            stage = float(row[2])
            if stage < 0:
                stage = None
        except ValueError:
            stage = None

        pot_record = entities.PotRecord(date, flow, stage)
        self.object.pot_records.append(pot_record)


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
        # Make descriptor name a valid python variable, by lowercasing, replacing spaces and hyphens with underscore,
        # e.g. `CENTROID NGR` -> `centroid_ngr`
        #      `RMED-1H`      -> `rmed_1h`
        name = row[0].lower().replace(' ', '_').replace('-', '_')

        # Standard numeric descriptors
        if name not in ['ihdtm_ngr', 'centroid_ngr']:
            value = float(row[1])
            # Filter out null-values
            if value == -9.999 or value == -999999:
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


class XmlCatchmentParser(object):
    """
    Parser for XML catchment files as exported from FEH CD-ROM (v3).

    An xml schema is not available.
    """

    def parse(self, file_name):
        """
        Parse entire file and return a :class:`Catchment` object.

        :param file_name: File path
        :type file_name: str
        :return: Parsed object
        :rtype: :class:`Catchment`
        """
        root = ET.parse(file_name).getroot()
        return self._parse(root)

    def parse_str(self, s):
        """
        Parse entire file and return a :class:`Catchment` object.

        :param file_name: File path
        :type file_name: str
        :return: Parsed object
        :rtype: :class:`Catchment`
        """
        root = ET.fromstring(s)
        return self._parse(root)

    def _parse(self, root):
        descr_node = root.find('CatchmentDescriptors')

        catchment = entities.Catchment()
        catchment.id = None
        country = descr_node.get('grid').lower()
        catchment.country = country if country in ['gb', 'ni'] else None
        catchment.area = float(descr_node.find('area').text)
        catchment.point = entities.Point(int(descr_node.get('x')), int(descr_node.get('y')))

        descr = catchment.descriptors
        descr.dtm_area = catchment.area
        descr.ihdtm_ngr = catchment.point
        centr_node = descr_node.find('CatchmentCentroid')
        descr.centroid_ngr = entities.Point(int(centr_node.get('x')), int(centr_node.get('y')))
        descr_keys = ['altbar', 'aspbar', 'aspvar', 'bfihost', 'dplbar', 'dpsbar', 'farl', 'fpext', 'ldp', 'propwet',
                      'rmed_1h', 'rmed_1d', 'rmed_2d', 'saar', 'saar4170', 'sprhost', 'urbconc1990', 'urbext1990',
                      'urbloc1990', 'urbconc2000', 'urbext2000', 'urbloc2000']
        for key in descr_keys:
            try:
                num_value = float(descr_node.find(key).text)
                if math.isnan(num_value):
                    num_value = None
                setattr(descr, key, num_value)
            except ValueError:
                pass # skip anything that can't be converted to float

        return catchment
