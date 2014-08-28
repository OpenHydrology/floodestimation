"""
Module containing flood estimation analysis methods, including QMED, growth curves etc.
"""
from math import log, floor, ceil


class QmedAnalysis(object):
    """
    Class to undertake QMED analyses.

    Example:

    >>> from floodestimation.catchment import Catchment
    >>> from floodestimation.analysis import QmedAnalysis
    >>> catchment = Catchment("Aberdeen", "River Dee")
    >>> catchment.descriptors = {'area': 1, 'bfihost': 0.50, 'sprhost': 50, 'saar': 1000, 'farl': 1, 'urbext': 0}
    >>> QmedAnalysis(catchment).qmed_all_methods()
    {'descriptors_1999': 0.2671386414098229, 'amax_records': None, 'channel_width': None, 'area': 1.172}

    """
    #: Methods available to estimate QMED, in order of best/preferred method
    methods = ('amax_records', 'descriptors_2008', 'descriptors_1999', 'area', 'channel_width')

    def __init__(self, catchment):
        """
        Creates a QMED analysis object.

        :param catchment: subject catchment
        :type: :class:`Catchment`
        :return:
        """

        self.catchment = catchment

    def qmed(self, method='best', **method_options):
        """
        Returns QMED estimate using best available methodology depending on what catchment attributes are available.

        The preferred/best order of methods is defined by :attr:`qmed_methods`. Alternatively, a method can be supplied
        e.g. `method='descriptors_1999'` to force the use of a particular method.

        :param method: methodology to use to estimate QMED. Default: automatically choose best method.
        :type: str
        :param method_options: any optional parameters for the QMED method function, e.g. `as_rural=True`

        :return: QMED in m³/s
        :type: float
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
        :type: float
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
        return 1 - 0.015 * log(2 * self.catchment.descriptors['area'])

    def _residual_soil(self):
        """
        Methodology source: FEH, Vol. 3, p. 14
        """
        return self.catchment.descriptors['bfihost'] \
               + 1.3 * (0.01 * self.catchment.descriptors['sprhost']) \
               - 0.987

    def _qmed_from_channel_width(self):
        """
        Return QMED estimate based on watercourse channel width.

        Methodology source: FEH, Vol. 3, p. 25

        :return: QMED in m³/s
        :type: float
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
        :type: float
        """
        try:
            return 1.172 * self.catchment.descriptors['area'] ** self._area_exponent()  # Area in km²
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    def _qmed_from_descriptors_1999(self, as_rural=False):
        """
        Return QMED estimation based on FEH catchment descriptors, 1999 methodology.

        Methodology source: FEH, Vol. 3, p. 14

        :param as_rural: assume catchment is fully rural. Default: false.
        :type: bool
        :return: QMED in m³/s
        :type: float
        """
        try:
            qmed_rural = 1.172 * self.catchment.descriptors['area'] ** self._area_exponent() \
                         * (self.catchment.descriptors['saar'] / 1000.0) ** 1.560 \
                         * self.catchment.descriptors['farl'] ** 2.642 \
                         * (self.catchment.descriptors['sprhost'] / 100.0) ** 1.211 * \
                         0.0198 ** self._residual_soil()
            if as_rural:
                return qmed_rural
            else:
                return qmed_rural * self.urban_adj_factor()
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    def _qmed_from_descriptors_2008(self, as_rural=False):
        """
        Return QMED estimation based on FEH catchment descriptors, 2008 methodology.

        Methodology source: TODO

        :param as_rural: assume catchment is fully rural. Default: false.
        :type: bool
        :return: QMED in m³/s
        :type: float
        """
        try:
            qmed_rural = 8.3062 * self.catchment.descriptors['area'] ** 0.8510 \
                         * 0.1536 ** (1000 / self.catchment.descriptors['saar']) \
                         * self.catchment.descriptors['farl'] ** 3.4451 \
                         * 0.0460 ** (self.catchment.descriptors['bfihost'] ** 2.0)
            if as_rural:
                return qmed_rural
            else:
                return qmed_rural * self.urban_adj_factor()
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    def _pruaf(self):
        """
        Returns percentage runoff urban adjustment factor.

        Methodology source: FEH, Vol. 3, p. 54
        """
        return 1 + 0.615 * self.catchment.descriptors['urbext'] * (70.0 / self.catchment.descriptors['sprhost'] - 1)

    def urban_adj_factor(self):
        """
        Returns urban adjustment factor (UAF) used to adjust QMED and growth curves.

        Methodology source: FEH, Vol. 3, p. 53

        :return: urban adjustment factor
        :rtype: float
        """
        return self._pruaf() * (1 + self.catchment.descriptors['urbext']) ** 0.83


class InsufficientDataError(BaseException):
    pass