"""
This module provides catchment related objects and methods.
"""
from floodestimation.analysis import QmedAnalysis


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

    def __init__(self, location, watercourse=None):
        # : Catchment outlet location name, e.g. `Aberdeen`
        self.location = location
        self._watercourse = watercourse
        #: FEH catchment descriptors as a dict
        self.descriptors = {}
        #: Width of the watercourse channel at the catchment outlet in m.
        self.channel_width = None
        #: List of annual maximum flow records as :class:`AmaxRecord` objects
        self.amax_records = []

    @property
    def watercourse(self):
        """
        Name of watercourse at the catchment outlet, e.g. `River Dee`
        """
        if self._watercourse:
            return self._watercourse
        else:
            return "Unknown watercourse"

    @watercourse.setter
    def watercourse(self, value):
        self._watercourse = value

    def qmed(self):
        """
        Returns QMED estimate using best available methodology depending on what catchment attributes are available.

        :return: QMED in m³/s
        :type: float
        """
        return QmedAnalysis(self).qmed()


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
        :type: :class:`datetime.date`
        :param flow: observed flow in  m³/s
        :type: float
        :param stage: observed water level in m above local datum
        :type: float
        """
        self.date = date

        # : Water year corresponding with :attr:`date`
        self.water_year = date.year
        if date.month < self.WATER_YEAR_FIRST_MONTH:
            self.water_year = date.year - 1

        self.flow = flow
        self.stage = stage