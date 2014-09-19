# -*- coding: utf-8 -*-

# Copyright (c) 2014  Neil Nutt <neilnutt[at]googlemail[dot]com> and
# Florenz A.P. Hollebrandse <f.a.p.hollebrandse@protonmail.ch>
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
Module containing flood estimation analysis methods, including QMED, growth curves etc.
"""
from math import log, floor, ceil, exp
# Current package imports


class QmedAnalysis(object):
    """
    Class to undertake QMED analyses.

    Example:

    >>> from floodestimation.entities import Catchment, Descriptors
    >>> from floodestimation.analysis import QmedAnalysis
    >>> catchment = Catchment("Aberdeen", "River Dee")
    >>> catchment.descriptors = Descriptors(dtm_area=1, bfihost=0.50, sprhost=50, saar=1000, farl=1, urbext=0)
    >>> QmedAnalysis(catchment).qmed_all_methods()
    {'descriptors': 0.5908579150223052, 'channel_width': None, 'area': 1.172, 'amax_records': None,
    'descriptors_1999': 0.2671386414098229}

    """
    #: Methods available to estimate QMED, in order of best/preferred method
    methods = ('amax_records', 'descriptors', 'descriptors_1999', 'area', 'channel_width')

    def __init__(self, catchment, gauged_catchment_collections=None):
        """
        Creates a QMED analysis object.

        :param catchment: subject catchment
        :type catchment: :class:`floodestimation.entities.Catchment`
        :param gauged_catchment_collections: catchment collections objects for retrieval of gauged data for donor
                                              analyses
        :type gauged_catchment_collections: :class:`floodestimation.collections.CatchmentCollections`
        """

        self.catchment = catchment
        self.gauged_catchments = gauged_catchment_collections

    def qmed(self, method='best', **method_options):
        """
        Returns QMED estimate using best available methodology depending on what catchment attributes are available.

        The preferred/best order of methods is defined by :attr:`qmed_methods`. Alternatively, a method can be supplied
        e.g. `method='descriptors_1999'` to force the use of a particular method.

        ================= ====================== =======================================================================
        `method`          `method_options`       notes
        ================= ====================== =======================================================================
        `amax_records`    n/a                    Simple median of annual maximum flow records using
                                                 `Catchment.amax_records`
        `descriptors`                            Synonym for `method=descriptors2008`.
        `descriptors2008` `as_rural=False`       FEH 2008 regression methodology using `Catchment.descriptors`. Setting
                          `donor_catchment=None` `as_rural=True` returns rural estimate and setting `donor_catchment` to
                                                 a specific :class:`Catchment` object **overrides** automatic selection
                                                 of the most suitable donor catchment.
        `descriptors1999` as_rural=False         FEH 1999 regression methodology.
        `area`            n/a                    Simplified FEH 1999 regression methodology using
                                                 `Cachment.descriptors.dtm_area` only.
        `channel_width`   n/a                    Emperical regression method using the river channel width only.
        ================= ====================== =======================================================================

        :param method: methodology to use to estimate QMED. Default: automatically choose best method.
        :type method: str
        :param method_options: any optional parameters for the QMED method function, e.g. `as_rural=True`
        :type method_options: kwargs

        :return: QMED in m³/s
        :rtype: float
        """
        if method == 'best':
            for method in self.methods:
                try:
                    # Return the first method that works
                    return getattr(self, '_qmed_from_' + method)(**method_options)
                except InsufficientDataError:
                    pass
            # In case none of them worked
            return None
        else:
            try:
                return getattr(self, '_qmed_from_' + method)(**method_options)
            except AttributeError:
                raise AttributeError("Method `{}` to estimate QMED does not exist.".format(method))

    def qmed_all_methods(self):
        """
        Returns a dict of QMED methods using all available methods.

        Available methods are defined in :attr:`qmed_methods`. The returned dict keys contain the method name, e.g.
        `amax_record` with value representing the corresponding QMED estimate in m³/s.

        :return: dict of QMED estimates
        :rtype: dict
        """
        result = {}
        for method in self.methods:
            try:
                result[method] = getattr(self, '_qmed_from_' + method)()
            except:
                result[method] = None
        return result

    def _qmed_from_amax_records(self):
        """
        Return QMED estimate based on annual maximum flow records.

        :return: QMED in m³/s
        :rtype: float
        """
        length = len(self.catchment.amax_records)
        if length < 2:
            raise InsufficientDataError("Insufficient annual maximum flow records available.")
        # Avoid numpy dependency at this stage...
        flow_sorted = sorted([record.flow for record in self.catchment.amax_records])
        return 0.5 * flow_sorted[int(floor(0.5 * (length - 1)))] + 0.5 * flow_sorted[int(ceil(0.5 * (length - 1)))]

    def _area_exponent(self):
        """
        Methodology source: FEH, Vol. 3, p. 14
        """
        return 1 - 0.015 * log(2 * self.catchment.descriptors.dtm_area)

    def _residual_soil(self):
        """
        Methodology source: FEH, Vol. 3, p. 14
        """
        return self.catchment.descriptors.bfihost \
               + 1.3 * (0.01 * self.catchment.descriptors.sprhost) \
               - 0.987

    def _qmed_from_channel_width(self):
        """
        Return QMED estimate based on watercourse channel width.

        Methodology source: FEH, Vol. 3, p. 25

        :return: QMED in m³/s
        :rtype: float
        """
        try:
            return 0.182 * self.catchment.channel_width ** 1.98
        except TypeError:
            raise InsufficientDataError("Catchment `channel_width` attribute must be set first.")

    def _qmed_from_area(self):
        """
        Return QMED estimate based on catchment area.

        TODO: add source of method

        :return: QMED in m³/s
        :rtype: float
        """
        try:
            return 1.172 * self.catchment.descriptors.dtm_area ** self._area_exponent()  # Area in km²
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    def _qmed_from_descriptors_1999(self, as_rural=False):
        """
        Return QMED estimation based on FEH catchment descriptors, 1999 methodology.

        Methodology source: FEH, Vol. 3, p. 14

        :param as_rural: assume catchment is fully rural. Default: false.
        :type as_rural: bool
        :return: QMED in m³/s
        :rtype: float
        """
        try:
            qmed_rural = 1.172 * self.catchment.descriptors.dtm_area ** self._area_exponent() \
                         * (self.catchment.descriptors.saar / 1000.0) ** 1.560 \
                         * self.catchment.descriptors.farl ** 2.642 \
                         * (self.catchment.descriptors.sprhost / 100.0) ** 1.211 * \
                         0.0198 ** self._residual_soil()
            if as_rural:
                return qmed_rural
            else:
                return qmed_rural * self.urban_adj_factor()
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    def _qmed_from_descriptors(self, **method_options):
        """
        Alias for current method to estimated QMED from catchment descriptors, currently: `descriptors_2008`

        :param method_options: Options to passed to actual QMED method function
        :type method_options: kwargs
        :return: QMED in m³/s
        :rtype: float
        """
        return self._qmed_from_descriptors_2008(**method_options)

    def _qmed_from_descriptors_2008(self, as_rural=False, donor_catchment=None):
        """
        Return QMED estimation based on FEH catchment descriptors, 2008 methodology.

        Methodology source: Science Report SC050050, p. 36

        :param as_rural: assume catchment is fully rural. Default: false.
        :type as rural: bool
        :param donor_catchment: override donor catchment to improve QMED catchment. If `None` (default), donor catchment
        will be searched automatically
        :type donor_catchment: :class:`Catchment`
        :return: QMED in m³/s
        :rtype: float
        """
        try:
            # Basis rural QMED from descriptors
            qmed_rural = 8.3062 * self.catchment.descriptors.dtm_area ** 0.8510 \
                         * 0.1536 ** (1000 / self.catchment.descriptors.saar) \
                         * self.catchment.descriptors.farl ** 3.4451 \
                         * 0.0460 ** (self.catchment.descriptors.bfihost ** 2.0)
            # Apply donor adjustment if donor provided
            if not donor_catchment:
                # For just now, pick the first suitable catchment.
                # TODO: implement algorithm to use multiple donors
                try:
                    donor_catchment = self.find_donor_catchments()[0]
                except IndexError:
                    pass
            if donor_catchment:
                qmed_rural *= self._donor_adj_factor(donor_catchment)
            if as_rural:
                return qmed_rural
            else:
                # Apply urbanisation adjustment
                return qmed_rural * self.urban_adj_factor()
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    def _pruaf(self):
        """
        Return percentage runoff urban adjustment factor.

        Methodology source: FEH, Vol. 3, p. 54
        """
        return 1 + 0.615 * self.catchment.descriptors.urbext * (70.0 / self.catchment.descriptors.sprhost - 1)

    def urban_adj_factor(self):
        """
        Return urban adjustment factor (UAF) used to adjust QMED and growth curves.

        Methodology source: FEH, Vol. 3, p. 53

        :return: urban adjustment factor
        :rtype: float
        """
        return self._pruaf() * (1 + self.catchment.descriptors.urbext) ** 0.83

    def _error_correlation(self, other_catchment):
        """
        Return model error correlation between subject catchment and other catchment.

        Methodology source: Science Report SC050050, p. 36

        :param other_catchment: catchment to calculate error correlation with
        :type other_catchment: :class:`Catchment`
        :return: correlation coefficient, r
        :rtype: float
        """
        distance = self.catchment.distance_to(other_catchment)
        return 0.4598 * exp(-0.0200 * distance) + (1 - 0.4598) * exp(-0.4785 * distance)

    def _donor_adj_factor(self, donor_catchment):
        """
        Return QMED adjustment factor using a donor catchment

        Methodology source: Science Report SC050050, p. 42

        :param donor_catchment: Catchment to use as a donor
        :type donor_catchment: :class:`Catchment`
        :return: Adjustment factor
        :rtype: float
        """
        donor_qmed_amax = QmedAnalysis(donor_catchment).qmed(method='amax_records')
        donor_qmed_descr = QmedAnalysis(donor_catchment).qmed(method='descriptors', as_rural=True)
        return (donor_qmed_amax / donor_qmed_descr) ** self._error_correlation(donor_catchment)

    def find_donor_catchments(self):
        """
        Return a suitable donor catchment to improve a QMED estimate based on catchment descriptors alone.

        :return: list of nearby catchments
        :rtype: :class:`floodestimation.entities.Catchment`
        """
        if self.gauged_catchments:
            return self.gauged_catchments.nearest_qmed_catchments(self.catchment)
        else:
            return []


class InsufficientDataError(BaseException):
    pass