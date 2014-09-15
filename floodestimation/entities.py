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
This module contains primary entities, including :class:`Catchment`, :class:`AmaxRecord` etc.
"""

from math import hypot
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, PickleType
from sqlalchemy.orm import relationship
# Current package imports
from .analysis import QmedAnalysis, InsufficientDataError
from . import db


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
    country = Column(String(2))
    #: Width of the watercourse channel at the catchment outlet in m.
    channel_width = Column(Float)
    #: Catchment area in km²
    area = Column(Float)
    #: Coordinates of catchment outlet as (E, N) tuple
    point = Column(PickleType)
    #: Whether this catchment can be used to estimate QMED at other similar catchments
    is_suitable_for_qmed = Column(Boolean)
    #: Whether this catchment's annual maximum flow data can be used in pooling group analyses
    is_suitable_for_pooling = Column(Boolean)
    #: List of annual maximum flow records as :class:`AmaxRecord` objects
    amax_records = relationship("AmaxRecord", order_by="AmaxRecord.water_year", backref="catchment")
    #: List of comments
    comments = relationship("Comment", order_by="Comment.title", backref="catchment")
    #: List of FEH catchment descriptors (one-to-one relationship)
    descriptors = relationship("Descriptors", uselist=False, backref="catchment")

    def __init__(self, location=None, watercourse=None):
        self.location = location
        self.watercourse = watercourse
        # Start with empty set of scriptors, so we always do `catchment.descriptors.name = value`
        self.descriptors = Descriptors()

    def qmed(self):
        """
        Returns QMED estimate using best available methodology depending on what catchment attributes are available.

        :return: QMED in m³/s
        :rtype: float
        """
        return QmedAnalysis(self).qmed()

    def distance_to(self, other_catchment):
        """
        Returns the distance between the centroids of two catchments.

        :param other_catchment: Catchment to calculate distance to
        :type other_catchment: :class:`Catchment`
        :return: Distance between the catchments in m.
        :rtype: float
        """
        try:
            if self.country == other_catchment.country:
                return hypot(self.descriptors.centroid_ngr[0] - other_catchment.descriptors.centroid_ngr[0],
                             self.descriptors.centroid_ngr[1] - other_catchment.descriptors.centroid_ngr[1])
            else:
                # If the catchments are in a different country (e.g. `ni` versus `gb`) then set distance to infinity.
                return float('+inf')
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")


class Descriptors(db.Base):
    """
    Set of FEH catchment descriptors.

    This is the complete set of name = value pairs in the `[DESCRIPTORS]` block in a CD3 file. All other parameters are
    directly attributes of :class:`Catchment`.

    Descriptors are used as follows:

    >>> from floodestimation.entities import Catchment
    >>> catchment = Catchment(...)
    >>> catchment.descriptors.dtm_area
    416.56
    >>> catchment.descriptors.centroid_ngr
    (317325, 699832)

    """
    __tablename__ = 'descriptors'
    #: One-to-one reference to :class:`Catchment` object
    catchment_id = Column(Integer, ForeignKey('catchments.id'), primary_key=True, nullable=False)
    #: Catchment outlet national grid reference as (E, N) tuple. :attr:`Catchment.country` indicates coordinate system.
    ihdtm_ngr = Column(PickleType)
    #: Catchment centre national grid reference as (E, N) tuple. :attr:`Catchment.country` indicates coordinate system.
    centroid_ngr = Column(PickleType)
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
    #: Lake, reservoir or loch parameter
    # TODO: add unit and range
    farl = Column(Float)
    #: Floodplain extent parameter
    # TODO: more precise description and unit and range
    fpext = Column(Float)
    # TODO: describe
    ldp = Column(Float)
    # TODO: describe
    propwet = Column(Float)
    # TODO: describe
    rmed_1h = Column(Float)
    # TODO: describe
    rmed_1d = Column(Float)
    # TODO: describe
    rmed_2d = Column(Float)
    #: Standard annual average rainfall in mm
    saar = Column(Float)
    #: Standard annual average rainfall in mm
    # TODO: describe better
    saar4170 = Column(Float)
    #: Standard percentage runoff based on Hydrology of Soil Types (HOST) data. Value between 0 and 100.
    sprhost = Column(Float)
    #: Urbanisation parameter, 1990 data
    # TODO: describe better
    urbconc1990 = Column(Float)
    #: Urbanisation parameter, 1990 data
    # TODO: describe better
    urbext1990 = Column(Float)
    #: Urbanisation parameter, 1990 data
    # TODO: describe better
    urbloc1990 = Column(Float)
    #: Urbanisation parameter, 2000 data
    # TODO: describe better
    urbconc2000 = Column(Float)
    #: Urbanisation parameter, 2000 data
    # TODO: describe better
    urbext2000 = Column(Float)
    #: Urbanisation parameter, 2000 data
    # TODO: describe better
    urbloc2000 = Column(Float)

    def get_urbext(self):
        return self.urbext2000

    def set_urbext(self, value):
        self.urbext2000 = value

    #: Alias for :attr:`urbext2000`
    urbext = property(get_urbext, set_urbext)


class AmaxRecord(db.Base):
    """
    A single annual maximum flow record.

    :attr:`Catchment.amax_records` is a list of :class:`AmaxRecord` objects.

    Example:

    >>> from floodestimation.entities import AmaxRecord
    >>> from datetime import date
    >>> record = AmaxRecord(date=date(1999,12,31), flow=51.2, stage=1.23)

    """
    __tablename__ = 'amaxrecords'
    #: Many-to-one reference to :class:`Catchment` object
    catchment_id = Column(Integer, ForeignKey('catchments.id'), primary_key=True, nullable=False)
    #: Water year or hydrological year (starts 1 October)
    water_year = Column(Integer, primary_key=True, nullable=False)
    #: Date at which maximum flow occured
    date = Column(Date)
    #: Observed flow in  m³/s
    flow = Column(Float)
    #: Observed water level in m above local datum
    stage = Column(Float)

    WATER_YEAR_FIRST_MONTH = 10

    def __init__(self, date, flow, stage):
        self.date = date
        if date:
            self.water_year = date.year
            # Jan-Sep is 'previous' water year
            if date.month < self.WATER_YEAR_FIRST_MONTH:
                self.water_year -= 1
        else:
            self.water_year = None
        self.flow = flow
        self.stage = stage

    def __repr__(self):
        return "{}: {:.1f} m³/s".format(self.water_year, self.flow)


class Comment(db.Base):
    """
    Comments on cachment contained in CD3 file. Each comment has a title (normally one of `station`, `catchment`,
    `qmed suitability` and `pooling suitability`) and content.

    :attr:`Catchment.comments` is a list of :class:`Comment` objects.

    Example:

    >>> from floodestimation.entities import Comment
    >>> comment = Comment(title="station", content="Velocity-area station on a straight reach ...")

    """
    __tablename__ = 'comments'
    #: Many-to-one reference to :class:`Catchment` object
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