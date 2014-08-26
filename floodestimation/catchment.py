"""
This module provides catchment related objects and methods.
"""
from math import log


class Catchment(object):
    """
    Catchment object include FEH catchment descriptors and additional information describing the catchment.
    """

    def __init__(self, location, watercourse=None):
        # : Catchment outlet location name, e.g. `Aberdeen`
        self.location = location
        self._watercourse = watercourse
        # : FEH catchment descriptors as a dict
        self.descriptors = {}
        # : Width of the watercourse channel at the catchment outlet in m.
        self.channel_width = None

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

    def _ae(self):
        return 1 - 0.015 * log(self.descriptors['area'] / 0.5)  # this is ln(2*A)

    def qmed_from_channel_width(self):
        """
        Return QMED estimate based on watercourse channel width.

        TODO: add source of method

        :return: QMED in m³/s
        :type: float
        """
        try:
            return 0.182 * self.channel_width ** 1.98
        except TypeError:
            raise Exception("Catchment `channel_width` attribute must be set first.")

    def qmed_from_area(self):
        """
        Return QMED estimate based on catchment area.

        TODO: add source of method

        :return: QMED in m³/s
        :type: float
        """
        try:
            return 1.172 * self.descriptors['area'] ** self._ae()
        except TypeError:
            raise Exception("Catchment `descriptors` attribute must be set first.")

    def qmed_from_descriptors_1999(self):
        reshost = self.descriptors['bfihost'] + 1.3 * (self.descriptors['sprhost'] / 100.0) - 0.987
        try:
            return 1.172 * self.descriptors['area'] ** self._ae() \
                   * (self.descriptors['saar'] / 1000.0) ** 1.560 \
                   * self.descriptors['farl'] ** 2.642 \
                   * (self.descriptors['sprhost'] / 100.0) ** 1.211 * \
                   0.0198 ** reshost
        except TypeError:
            raise Exception("Catchment `descriptors` attribute must be set first.")
