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
This module contains the core components or entities, including :class:`.Catchment`, :class:`.AmaxRecord` etc.

Note that all entities are subclasses of :class:`floodestimation.db.Base` which is an SQL Alchemy base class to enable
saving to a (sqlite) database. All class attributes therefore are :class:`sqlalchemy.Column` objects e.g.
`Column(Float)`, `Column(String)`, etc. Attribute values can simply be set like normal, e.g. `catchment.watercourse =
"River Dee"`.

"""

from math import hypot, atan
from datetime import timedelta
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, SmallInteger, type_coerce
from sqlalchemy.orm import relationship, composite
from sqlalchemy.ext.mutable import MutableComposite
from sqlalchemy.ext.hybrid import hybrid_method
# Current package imports
from .analysis import QmedAnalysis, InsufficientDataError
from . import db


class Point(MutableComposite):
    """
    Point coordinate object

    Example:

    >>> from floodestimation.entities import Point
    >>> point = Point(123000, 456000)

    Coordinates systems are currently not supported. Instead use `Catchment.country = 'gb'` etc.

    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        # alert all parents to the change
        self.changed()

    def __composite_values__(self):
        return self.x, self.y

    def __eq__(self, other):
        return isinstance(other, Point) and \
            other.x == self.x and \
            other.y == self.y

    def __ne__(self, other):
        return not self.__eq__(other)


class Catchment(db.Base):
    """
    Catchment object include FEH catchment descriptors and additional information describing the catchment.

    Example:

    >>> from floodestimation.entities import Catchment, Descriptors
    >>> catchment = Catchment("Aberdeen", "River Dee")
    >>> catchment.channel_width = 1
    >>> catchment.descriptors = Descriptors(dtm_area=1, bfihost=0.50, sprhost=50, saar=1000, farl=1, urbext=0}
    >>> catchment.qmed()
    0.2671386414098229

    """
    __tablename__ = 'catchments'

    #: Gauging station number
    id = Column(Integer, primary_key=True)
    #: Catchment outlet location name, e.g. `Aberdeen`
    location = Column(String)
    #: Name of watercourse at the catchment outlet, e.g. `River Dee`
    watercourse = Column(String)
    #: Abbreviation of country, e.g. `gb`, `ni`.
    country = Column(String(2), index=True)
    #: Width of the watercourse channel at the catchment outlet in m.
    channel_width = Column(Float)
    #: Catchment area in km²
    area = Column(Float)

    point_x = Column(Integer, index=True)
    point_y = Column(Integer, index=True)
    #: Coordinates of catchment outlet as :class:`.Point` object
    point = composite(Point, point_x, point_y)

    #: Whether this catchment can be used to estimate QMED at other similar catchments
    is_suitable_for_qmed = Column(Boolean, index=True)
    #: Whether this catchment's annual maximum flow data can be used in pooling group analyses
    is_suitable_for_pooling = Column(Boolean, index=True)
    #: List of annual maximum flow records as :class:`.AmaxRecord` objects
    amax_records = relationship("AmaxRecord", order_by="AmaxRecord.water_year", cascade="all, delete-orphan",
                                backref="catchment")
    #: Peaks-over-threshold dataset (one-to-one relationship)
    pot_dataset = relationship("PotDataset", uselist=False, cascade="all, delete-orphan", backref="catchment")
    #: List of comments
    comments = relationship("Comment", order_by="Comment.title", cascade="all, delete-orphan", backref="catchment")
    #: FEH catchment descriptors (one-to-one relationship)
    descriptors = relationship("Descriptors", uselist=False, cascade="all, delete-orphan", backref="catchment")

    def __init__(self, location=None, watercourse=None):
        self.location = location
        self.watercourse = watercourse
        self.amax_records = []
        # Start with empty set of descriptors, so we always do `catchment.descriptors.name = value`
        self.descriptors = Descriptors()
          
    def qmed(self):
        """
        Returns QMED estimate using best available methodology depending on what catchment attributes are available.

        :return: QMED in m³/s
        :rtype: float
        """
        return QmedAnalysis(self).qmed()

    @hybrid_method
    def distance_to(self, other_catchment):
        """
        Returns the distance between the centroids of two catchments in kilometers.

        :param other_catchment: Catchment to calculate distance to
        :type other_catchment: :class:`.Catchment`
        :return: Distance between the catchments in km.
        :rtype: float
        """
        try:
            if self.country == other_catchment.country:
                try:
                    return 0.001 * hypot(self.descriptors.centroid_ngr.x - other_catchment.descriptors.centroid_ngr.x,
                                         self.descriptors.centroid_ngr.y - other_catchment.descriptors.centroid_ngr.y)
                except TypeError:
                    # In case no centroid available, just return infinity which is helpful in most cases
                    return float('+inf')
            else:
                # If the catchments are in a different country (e.g. `ni` versus `gb`) then set distance to infinity.
                return float('+inf')
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    @distance_to.expression
    def distance_to(cls, other_catchment):
        return type_coerce(
            1e-6 * ((Descriptors.centroid_ngr_x - other_catchment.descriptors.centroid_ngr_x) *
                    (Descriptors.centroid_ngr_x - other_catchment.descriptors.centroid_ngr_x) +
                    (Descriptors.centroid_ngr_y - other_catchment.descriptors.centroid_ngr_y) *
                    (Descriptors.centroid_ngr_y - other_catchment.descriptors.centroid_ngr_y)),
            Float())

    def __repr__(self):
        return "{} at {} ({})".format(self.watercourse, self.location, self.id)


class Descriptors(db.Base):
    """
    Set of FEH catchment descriptors.

    This is the complete set of name = value pairs in the `[DESCRIPTORS]` block in a CD3 file. All other parameters are
    directly attributes of :class:`.Catchment`.

    Descriptors are used as follows:

    >>> from floodestimation.entities import Catchment
    >>> catchment = Catchment(...)
    >>> catchment.descriptors.dtm_area
    416.56
    >>> catchment.descriptors.centroid_ngr
    (317325, 699832)

    """
    __tablename__ = 'descriptors'

    #: One-to-one reference to corresponding :class:`.Catchment` object
    catchment_id = Column(Integer, ForeignKey('catchments.id'), primary_key=True, nullable=False)

    ihdtm_ngr_x = Column(Integer)
    ihdtm_ngr_y = Column(Integer)
    #: Catchment outlet national grid reference as :class:`.Point` object. :attr:`.Catchment.country` indicates
    #: coordinate system.
    ihdtm_ngr = composite(Point, ihdtm_ngr_x, ihdtm_ngr_y)

    centroid_ngr_x = Column(Integer, index=True)
    centroid_ngr_y = Column(Integer, index=True)
    #: Catchment centre national grid reference as :class:`.Point` object. :attr:`.Catchment.country` indicates
    #: coordinate system.
    centroid_ngr = composite(Point, centroid_ngr_x, centroid_ngr_y)

    #: Surface area in km² based on digital terrain model data
    dtm_area = Column(Float)
    #: Mean elevation in m
    altbar = Column(Float)
    #: Mean aspect (orientation) in degrees
    aspbar = Column(Float)
    #: Aspect variance in degrees
    aspvar = Column(Float)
    #: Base flow index based on Hydrology of Soil Types (HOST) data. Value between 0 and 1.
    bfihost = Column(Float)
    #: Mean drainage path length in km
    dplbar = Column(Float)
    #: Mean drainage path slope (dimensionless)
    dpsbar = Column(Float)
    #: Lake, reservoir or loch flood attenuation index
    farl = Column(Float)
    #: Floodplain extent parameter
    fpext = Column(Float)
    #: Longest drainage path length in km
    ldp = Column(Float)
    #: Proportion of time soils are wet index
    propwet = Column(Float)
    #: Median annual maximum 1 hour rainfall in mm
    rmed_1h = Column(Float)
    #: Median annual maximum 1 day rainfall in mm
    rmed_1d = Column(Float)
    #: Median annual maximum 2 day rainfall in mm
    rmed_2d = Column(Float)
    #: Standard annual average rainfall in mm, 1961-1990 average
    saar = Column(Float)
    #: Standard annual average rainfall in mm, 1941-1970 average
    saar4170 = Column(Float)
    #: Standard percentage runoff based on Hydrology of Soil Types (HOST) data. Value between 0 and 100.
    sprhost = Column(Float)
    #: Urbanisation concentration index, 1990 data
    urbconc1990 = Column(Float)
    #: Urbanisation extent index, 1990 data
    urbext1990 = Column(Float)
    #: Urbanisation location within catchment index, 1990 data
    urbloc1990 = Column(Float)
    #: Urbanisation concentration index, 2000 data
    urbconc2000 = Column(Float)
    #: Urbanisation extent index, 2000 data
    urbext2000 = Column(Float, index=True)
    #: Urbanisation location within catchment index, 2000 data
    urbloc2000 = Column(Float)

    def urbext(self, year):
        """
        Estimate the `urbext2000` parameter for a given year assuming a nation-wide urbanisation curve.

        Methodology source: eqn 5.5, report FD1919/TR

        :param year: Year to provide estimate for
        :type year: float
        :return: Urban extent parameter
        :rtype: float
        """

        # Decimal places increased to ensure year 2000 corresponds with 1
        urban_expansion = 0.7851 + 0.2124 * atan((year - 1967.5) / 20.331792998)
        try:
            return self.catchment.descriptors.urbext2000 * urban_expansion
        except TypeError:
            # Sometimes urbext2000 is not set, assume zero
            return 0


class AmaxRecord(db.Base):
    """
    A single annual maximum flow record.

    :attr:`.Catchment.amax_records` is a list of :class:`.AmaxRecord` objects.

    Example:

    >>> from floodestimation.entities import AmaxRecord
    >>> from datetime import date
    >>> record = AmaxRecord(date=date(1999,12,31), flow=51.2, stage=1.23)

    """
    __tablename__ = 'amaxrecords'
    #: Many-to-one reference to corresponding :class:`.Catchment` object
    catchment_id = Column(Integer, ForeignKey('catchments.id'), primary_key=True, nullable=False)
    #: Water year or hydrological year (starts 1 October)
    water_year = Column(Integer, primary_key=True, nullable=False)
    #: Date at which maximum flow occured
    date = Column(Date)
    #: Observed flow in  m³/s
    flow = Column(Float)
    #: Observed water level in m above local datum
    stage = Column(Float)
    #: Data quality flag. 0 (default): valid value, 1: invalid value, 2: rejected record.
    flag = Column(SmallInteger, index=True, default=0)

    WATER_YEAR_FIRST_MONTH = 10  # Should provide flexibility to use different first months

    def __init__(self, date, flow, stage, flag=0):
        self.date = date
        self.water_year = self.water_year_from_date(date)
        self.flow = flow
        self.stage = stage
        self.flag = flag

    def __repr__(self):
        return "{}: {:.1f} m³/s".format(self.water_year, self.flow)

    @classmethod
    def water_year_from_date(cls, date):
        if date.month >= cls.WATER_YEAR_FIRST_MONTH:
            return date.year
        else:
            # Jan-Sep is 'previous' water year
            return date.year - 1


class PotPeriod(object):
    def __init__(self, start_date, end_date):
        #: Start date of flow record
        self.start_date = start_date
        #: End date of flow record (inclusive)
        self.end_date = end_date

    def period_length(self):
        """
        Return record length in years.
        """
        return ((self.end_date - self.start_date).days + 1) / 365

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __repr__(self):
        return "PotPeriod {} to {}".format(self.start_date, self.end_date)


class PotDataset(db.Base):
    """
    A peaks-over-threshold (POT) dataset including a list of :class:`.PotRecord` objects and some metadata such as start
    and end of record.
    """
    __tablename__ = 'potdatasets'
    #: One-to-one reference to corresponding :class:`.Catchment` object
    catchment_id = Column(Integer, ForeignKey('catchments.id'), primary_key=True, nullable=False)
    #: Start date of flow record
    start_date = Column(Date)
    #: End date of flow record (inclusive)
    end_date = Column(Date)
    #: Flow threshold in m³/s
    threshold = Column(Float)
    #: List of peaks-over-threshold records as :class:`.PotRecord` objects
    pot_records = relationship('PotRecord', order_by='PotRecord.date', cascade="all, delete-orphan",
                               backref='catchment')
    #: List of peaks-over-threshold records as :class:`.PotDataGap` objects
    pot_data_gaps = relationship('PotDataGap', order_by='PotDataGap.start_date', cascade="all, delete-orphan",
                                 backref='catchment')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pot_records = []
        self.pot_data_gaps = []

    def record_length(self):
        """
        Return record length in years, including data gaps.
        """
        return ((self.end_date - self.start_date).days + 1) / 365 - self.total_gap_length()

    def total_gap_length(self):
        """
        Return the total length of POT gaps in years.
        """
        return sum(gap.gap_length() for gap in self.pot_data_gaps)

    def continuous_periods(self):
        """
        Return a list of continuous data periods by removing the data gaps from the overall record.
        """
        result = []

        # For the first period
        start_date = self.start_date
        for gap in self.pot_data_gaps:
            end_date = gap.start_date - timedelta(days=1)
            result.append(PotPeriod(start_date, end_date))
            # For the next period
            start_date = gap.end_date + timedelta(days=1)
        # For the last period
        end_date = self.end_date
        result.append(PotPeriod(start_date, end_date))

        return result


class PotDataGap(db.Base):
    """
    A gap (period) in the peaks-over-threshold (POT) records.
    """
    __tablename__ = 'potdatagaps'
    # We should really have catchment_id + start_date as primary key but unfortunately there are duplicates in the NRFA
    # dataset!
    id = Column(Integer, primary_key=True)
    #: Many-to-one reference to corresponding :class:`.Catchment` object
    catchment_id = Column(Integer, ForeignKey('potdatasets.catchment_id'), nullable=False, index=True)
    #: Start date of gap
    start_date = Column(Date, nullable=False)
    #: End date of gap (inclusive)
    end_date = Column(Date, nullable=False)

    def gap_length(self):
        """
        Return length of data gap in years.
        """
        return ((self.end_date - self.start_date).days + 1) / 365


class PotRecord(db.Base):
    """
    A single peaks-over-threshold (POT) flow record.

    Example:

    >>> from floodestimation.entities import PotRecord
    >>> from datetime import date
    >>> record = PotRecord(date=date(1999,12,31), flow=51.2, stage=1.23)

    """
    __tablename__ = 'potrecords'
    # We should really have catchment_id + date as primary key but unfortunately there are duplicates in the NRFA
    # dataset!
    id = Column(Integer, primary_key=True)
    #: Many-to-one reference to corresponding :class:`.Catchment` object
    catchment_id = Column(Integer, ForeignKey('potdatasets.catchment_id'), nullable=False, index=True)
    #: Date at which flow occured
    date = Column(Date, nullable=False)
    #: Observed flow in m³/s
    flow = Column(Float)
    #: Observed water level in m above local datum
    stage = Column(Float)

    def __init__(self, date, flow, stage):
        self.date = date
        self.flow = flow
        self.stage = stage

    def __repr__(self):
        return "{}: {:.1f} m³/s".format(self.date, self.flow)


class Comment(db.Base):
    """
    Comments on cachment contained in CD3 file. Each comment has a title (normally one of `station`, `catchment`,
    `qmed suitability` and `pooling suitability`) and content.

    :attr:`.Catchment.comments` is a list of :class:`.Comment` objects.

    Example:

    >>> from floodestimation.entities import Comment
    >>> comment = Comment(title="station", content="Velocity-area station on a straight reach ...")

    """
    __tablename__ = 'comments'
    #: Many-to-one reference to corresponding :class:`.Catchment` object
    catchment_id = Column(Integer, ForeignKey('catchments.id'), primary_key=True, nullable=False)
    #: Comment title, e.g. `station`
    title = Column(String, primary_key=True, nullable=False)
    #: Comment, e.g. `Velocity-area station on a straight reach ...`
    content = Column(String)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return "{}: {}".format(self.title, self.content)

