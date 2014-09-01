"""
This module provides catchment related objects and methods.
"""
from floodestimation.analysis import QmedAnalysis, InsufficientDataError
from math import hypot


class Catchment(object):
    """
    Catchment object include FEH catchment descriptors and additional information describing the catchment.

    Example:

    >>> from floodestimation.catchment import Catchment
    >>> catchment = Catchment("Aberdeen", "River Dee")
    >>> catchment.channel_width = 1
    >>> catchment.descriptors = {'area': 1, 'bfihost': 0.50, 'sprhost': 50, 'saar': 1000, 'farl': 1, 'urbext': 0}
    >>> catchment.qmed()
    0.2671386414098229

    """

    def __init__(self, location=None, watercourse=None):
        #: Gauging station number
        self.id = None
        #: Catchment outlet location name, e.g. `Aberdeen`
        self.location = location
        #: Name of watercourse at the catchment outlet, e.g. `River Dee`
        self.watercourse = watercourse
        #: FEH catchment descriptors as a dict
        self.descriptors = {}
        #: Width of the watercourse channel at the catchment outlet in m.
        self.channel_width = None
        #: List of annual maximum flow records as :class:`AmaxRecord` objects
        self.amax_records = []
        self.comments = {}

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
            return hypot(self.descriptors['centroid'][0] - other_catchment.descriptors['centroid'][0],
                         self.descriptors['centroid'][1] - other_catchment.descriptors['centroid'][1])
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")


class AmaxRecord(object):
    """
    A single annual maximum flow record.

    Example:

    >>> from floodestimation.catchment import AmaxRecord
    >>> from datetime import date
    >>> record = AmaxRecord(date=date(1999,12,31), flow=51.2, stage=1.23)

    """

    WATER_YEAR_FIRST_MONTH = 10

    def __init__(self, date, flow, stage):
        """

        :param date: date of maximum flow occuring
        :type date: :class:`datetime.date`
        :param flow: observed flow in  m³/s
        :type flow: float
        :param stage: observed water level in m above local datum
        :rtype: float
        """
        self.date = date
        if date:
            self.water_year = date.year
            if date.month < self.WATER_YEAR_FIRST_MONTH:
                self.water_year -= 1
        else:
            self.water_year = None
        self.flow = flow
        self.stage = stage

    def __str__(self):
        return("{}: {:.1f} m³/s".format(self.water_year, self.flow))

    def __repr__(self):
        return str(self)