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
from math import log, exp, sqrt, floor, atan
from datetime import date
import copy
import lmoments3 as lm
import lmoments3.distr as lm_distr
import numpy as np
from numpy import linalg
from scipy import optimize


def valid_flows_array(catchment):
    """
    Return array of valid flows (i.e. excluding rejected years etc)

    :param catchment: gauged catchment with amax_records set
    :type catchment: :class:`floodestimation.entities.Catchment`
    :return: 1D array of flow values
    :rtype: :class:`numpy.ndarray`
    """
    return np.array([record.flow for record in catchment.amax_records if record.flag == 0])


class Analysis(object):
    """
    Generic analysis object
    """

    def __init__(self, year=None, results_log=None):
        """
        :param year: Year to base analysis on. Default: current year.
        :type year: float
        :param results_log: Dict to store intermediate results
        :type results_log: dict
        """

        self.year = year or date.today().year

        if results_log is not None:
            self.results_log = results_log
        else:
            self.results_log = {}


class QmedAnalysis(Analysis):
    """
    Class to undertake QMED analyses.

    Example:

    >>> from floodestimation.entities import Catchment, Descriptors
    >>> from floodestimation.analysis import QmedAnalysis
    >>> catchment = Catchment("Aberdeen", "River Dee")
    >>> catchment.descriptors = Descriptors(dtm_area=1, bfihost=0.50, sprhost=50, saar=1000, farl=1, urbext2000=0)
    >>> QmedAnalysis(catchment).qmed_all_methods()
    {'descriptors': 0.5908579150223052, 'pot_records': None, 'channel_width': None,
    'descriptors_1999': 0.2671386414098229, 'area': 1.172, 'amax_records': None}

    """
    # : Methods available to estimate QMED, in order of best/preferred method
    methods = ('amax_records', 'pot_records', 'descriptors', 'descriptors_1999', 'area', 'channel_width')

    def __init__(self, catchment, gauged_catchments=None, year=None, results_log=None):
        """
        :param catchment: subject catchment
        :type catchment: :class:`.entities.Catchment`
        :param gauged_catchments: catchment collections objects for retrieval of gauged data for donor analyses
        :type gauged_catchments: :class:`.collections.CatchmentCollections`
        """
        Analysis.__init__(self, year, results_log)

        self.catchment = catchment
        self.gauged_catchments = gauged_catchments

    def qmed(self, method='best', **method_options):
        """
        Return QMED estimate using best available methodology depending on what catchment attributes are available.

        The preferred/best order of methods is defined by :attr:`qmed_methods`. Alternatively, a method can be supplied
        e.g. `method='descriptors_1999'` to force the use of a particular method.

        ================= ======================= ======================================================================
        `method`          `method_options`        notes
        ================= ======================= ======================================================================
        `amax_records`    n/a                     Simple median of annual maximum flow records using
                                                  `Catchment.amax_records`.
        `pot_records`     n/a                     Uses peaks-over-threshold (POT) flow records. Suitable for flow
                                                  records shorter than 14 years.
        `descriptors`                             Synonym for `method=descriptors2008`.
        `descriptors2008` `as_rural=False`        FEH 2008 regression methodology using `Catchment.descriptors`. Setting
                          `donor_catchments=None` `as_rural=True` returns rural estimate and setting `donor_catchments`
                                                  to a specific list of :class:`Catchment` object **overrides**
                                                  automatic selection of the most suitable donor catchment. An empty
                                                  list forces no donors to be used at all.
        `descriptors1999` as_rural=False          FEH 1999 regression methodology.
        `area`            n/a                     Simplified FEH 1999 regression methodology using
                                                  `Cachment.descriptors.dtm_area` only.
        `channel_width`   n/a                     Emperical regression method using the river channel width only.
        ================= ======================= ======================================================================

        :param method: methodology to use to estimate QMED. Default: automatically choose best method.
        :type method: str
        :param method_options: any optional parameters for the QMED method function, e.g. `as_rural=True`
        :type method_options: kwargs

        :return: QMED in m³/s
        :rtype: float
        """
        if method == 'best':
            # Rules for gauged catchments
            if self.catchment.pot_dataset:
                if self.catchment.amax_records:
                    if len(self.catchment.amax_records) <= self.catchment.pot_dataset.record_length() < 14:
                        use_method = 'pot_records'
                    elif len(self.catchment.amax_records) >= 2:
                        use_method = 'amax_records'
                    else:
                        use_method = None
                elif self.catchment.pot_dataset.record_length() >= 1:
                    use_method = 'pot_records'
                else:
                    use_method = None
            elif len(self.catchment.amax_records) >= 2:
                use_method = 'amax_records'
            else:
                use_method = None  # None of the gauged methods will work
            if use_method:
                self.results_log['method'] = use_method
                return getattr(self, '_qmed_from_' + use_method)()

            # Ungauged methods
            for method in self.methods[1:]:
                try:
                    # Return the first method that works
                    self.results_log['method'] = method
                    return getattr(self, '_qmed_from_' + method)(**method_options)
                except (TypeError, InsufficientDataError):
                    pass
            # In case none of them worked
            return None

        else:
            # A specific method has been requested
            try:
                self.results_log['method'] = method
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
        valid_flows = valid_flows_array(self.catchment)
        n = len(valid_flows)
        if n < 2:
            raise InsufficientDataError("Insufficient annual maximum flow records available for catchment {}."
                                        .format(self.catchment.id))
        return np.median(valid_flows)

    def _qmed_from_pot_records(self):
        """
        Return QMED estimate based on peaks-over-threshold (POT) records.

        Methodology source: FEH, Vol. 3, pp. 77-78

        :return: QMED in m³/s
        :rtype: float
        """
        pot_dataset = self.catchment.pot_dataset
        if not pot_dataset:
            raise InsufficientDataError("POT dataset must be set for catchment {} to estimate QMED from POT data."
                                        .format(self.catchment.id))

        complete_year_records, length = self._complete_pot_years(pot_dataset)
        if length < 1:
            raise InsufficientDataError("Insufficient POT flow records available for catchment {}."
                                        .format(self.catchment.id))

        position = 0.790715789 * length + 0.539684211
        i = floor(position)
        w = 1 + i - position  # This is equivalent to table 12.1!

        flows = [record.flow for record in complete_year_records]
        flows.sort(reverse=True)

        return w * flows[i - 1] + (1 - w) * flows[i]

    def _pot_month_counts(self, pot_dataset):
        """
        Return a list of 12 sets. Each sets contains the years included in the POT record period.

        :param pot_dataset: POT dataset (records and meta data)
        :type pot_dataset: :class:`floodestimation.entities.PotDataset`
        """
        periods = pot_dataset.continuous_periods()
        result = [set() for x in range(12)]
        for period in periods:
            year = period.start_date.year
            month = period.start_date.month
            while True:
                # Month by month, add the year
                result[month - 1].add(year)
                # If at end of period, break loop
                if year == period.end_date.year and month == period.end_date.month:
                    break
                # Next month (and year if needed)
                month += 1
                if month == 13:
                    month = 1
                    year += 1
        return result

    def _complete_pot_years(self, pot_dataset):
        """
        Return a tuple of a list of :class:`PotRecord`s filtering out part-complete years; and the number of complete
        years.

        This method creates complete years by ensuring there is an equal number of each month in the entire record,
        taking into account data gaps. A month is considered to be covered by the record if there is at least a single
        day of the month in any continuous period. (There doesn't have to be a record!) "Leftover" months not needed are
        left at the beginning of the record, i.e. recent records are prioritised over older records.

        :param pot_dataset: POT dataset (records and meta data)
        :type pot_dataset: :class:`floodestimation.entities.PotDataset`
        :return: list of POT records
        :rtype: list of :class:`floodestimation.entities.PotRecord`
        """
        # Create a list of 12 sets, one for each month. Each set represents the years for which the POT record includes
        # a particular month.
        month_counts = self._pot_month_counts(pot_dataset)
        # Number of complete years
        n = min([len(month) for month in month_counts])
        # Use the last available years only such that there are equal numbers of each month; i.e. part years are
        # excluded at the beginning of the record
        years_to_use = [sorted(month)[-n:] for month in month_counts]
        return (
            [record for record in pot_dataset.pot_records if record.date.year in years_to_use[record.date.month - 1]],
            n)

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

    def _qmed_from_descriptors_2008(self, as_rural=False, donor_catchments=None):
        """
        Return QMED estimation based on FEH catchment descriptors, 2008 methodology.

        Methodology source: Science Report SC050050, p. 36

        :param as_rural: assume catchment is fully rural. Default: false.
        :type as rural: bool
        :param donor_catchments: override donor catchment to improve QMED catchment. If `None` (default),
        donor catchment will be searched automatically, if empty list, no donors will be used.
        :type donor_catchments: :class:`Catchment`
        :return: QMED in m³/s
        :rtype: float
        """
        try:
            # Basis rural QMED from descriptors
            lnqmed_rural = 2.1170 \
                           + 0.8510 * log(self.catchment.descriptors.dtm_area) \
                           - 1.8734 * 1000 / self.catchment.descriptors.saar \
                           + 3.4451 * log(self.catchment.descriptors.farl) \
                           - 3.0800 * self.catchment.descriptors.bfihost ** 2.0
            qmed_rural = exp(lnqmed_rural)

            # Log intermediate results
            self.results_log['qmed_descr_rural'] = qmed_rural

            if donor_catchments is None:
                # If no donor catchments are provided, find the nearest 25
                donor_catchments = self.find_donor_catchments()
            if donor_catchments:
                # If found multiply rural estimate with weighted adjustment factors from all donors

                weights = self._vec_alpha(donor_catchments)
                errors = self._vec_lnqmed_residuals(donor_catchments)
                correction = np.dot(weights, errors)

                lnqmed_rural += correction
                qmed_rural = exp(lnqmed_rural)

                # Log intermediate results
                self.results_log['donors'] = donor_catchments
                for i, donor in enumerate(self.results_log['donors']):
                    donor.weight = weights[i]
                    donor.factor = exp(errors[i])
                self.results_log['donor_adj_factor'] = exp(correction)
                self.results_log['qmed_adj_rural'] = qmed_rural

            if as_rural:
                return qmed_rural
            else:
                # Apply urbanisation adjustment
                urban_adj_factor = self.urban_adj_factor()

                # Log intermediate results
                self.results_log['qmed_descr_urban'] = self.results_log['qmed_descr_rural'] * urban_adj_factor
                return qmed_rural * urban_adj_factor
        except (TypeError, KeyError):
            raise InsufficientDataError("Catchment `descriptors` attribute must be set first.")

    def _pruaf(self):
        """
        Return percentage runoff urban adjustment factor.

        Methodology source: eqn. 6, Kjeldsen 2010
        """
        return 1 + 0.47 * self.catchment.descriptors.urbext(self.year) \
                   * self.catchment.descriptors.bfihost / (1 - self.catchment.descriptors.bfihost)

    def urban_adj_factor(self):
        """
        Return urban adjustment factor (UAF) used to adjust QMED and growth curves.

        Methodology source: eqn. 8, Kjeldsen 2010

        :return: urban adjustment factor
        :rtype: float
        """
        urbext = self.catchment.descriptors.urbext(self.year)
        result = self._pruaf() ** 2.16 * (1 + urbext) ** 0.37
        self.results_log['urban_extent'] = urbext
        self.results_log['urban_adj_factor'] = result
        return result

    @staticmethod
    def _dist_corr(dist, phi1, phi2, phi3):
        """
        Generic distance-decaying correlation function

        :param dist: Distance between catchment centrolds in km
        :type dist: float
        :param phi1: Decay function parameters 1
        :type phi1: float
        :param phi2: Decay function parameters 2
        :type phi2: float
        :param phi3: Decay function parameters 3
        :type phi3: float
        :return: Correlation coefficient, r
        :rtype: float
        """
        return phi1 * exp(-phi2 * dist) + (1 - phi1) * exp(-phi3 * dist)

    def _model_error_corr(self, catchment1, catchment2):
        """
        Return model error correlation between subject catchment and other catchment.

        Methodology source: Kjeldsen & Jones, 2009, table 3

        :param catchment1: catchment to calculate error correlation with
        :type catchment1: :class:`Catchment`
        :param catchment2: catchment to calculate error correlation with
        :type catchment2: :class:`Catchment`
        :return: correlation coefficient, r
        :rtype: float
        """
        dist = catchment1.distance_to(catchment2)
        return self._dist_corr(dist, 0.3998, 0.0283, 0.9494)

    def _lnqmed_corr(self, catchment1, catchment2):
        """
        Return model error correlation between subject catchment and other catchment.

        Methodology source: Kjeldsen & Jones, 2009, fig 3

        :param catchment1: catchment to calculate correlation with
        :type catchment1: :class:`Catchment`
        :param catchment2: catchment to calculate correlation with
        :type catchment2: :class:`Catchment`
        :return: correlation coefficient, r
        :rtype: float
        """
        dist = catchment1.distance_to(catchment2)
        return self._dist_corr(dist, 0.2791, 0.0039, 0.0632)

    def _vec_b(self, donor_catchments):
        """
        Return vector ``b`` of model error covariances to estimate weights

        Methodology source: Kjeldsen, Jones and Morris, 2009, eqs 3 and 10

        :param donor_catchments: Catchments to use as donors
        :type donor_catchments: list of :class:`Catchment`
        :return: Model error covariance vector
        :rtype: :class:`numpy.ndarray`
        """
        p = len(donor_catchments)
        b = 0.1175 * np.ones(p)
        for i in range(p):
            b[i] *= self._model_error_corr(self.catchment, donor_catchments[i])
        return b

    @staticmethod
    def _beta(catchment):
        """
        Return beta, the GLO scale parameter divided by loc parameter estimated using simple regression model

        Methodology source: Kjeldsen & Jones, 2009, table 2

        :param catchment: Catchment to estimate beta for
        :type catchment: :class:`Catchment`
        :return: beta
        :rtype: float
        """
        lnbeta = -1.1221 \
                 - 0.0816 * log(catchment.descriptors.dtm_area) \
                 - 0.4580 * log(catchment.descriptors.saar / 1000) \
                 + 0.1065 * log(catchment.descriptors.bfihost)
        return exp(lnbeta)

    def _matrix_sigma_eta(self, donor_catchments):
        """
        Return model error coveriance matrix Sigma eta

        Methodology source: Kjelsen, Jones & Morris 2014, eqs 2 and 3

        :param donor_catchments: Catchments to use as donors
        :type donor_catchments: list of :class:`Catchment`
        :return: 2-Dimensional, symmetric covariance matrix
        :rtype: :class:`numpy.ndarray`
        """
        p = len(donor_catchments)
        sigma = 0.1175 * np.ones((p, p))
        for i in range(p):
            for j in range(p):
                if i != j:
                    sigma[i, j] *= self._model_error_corr(donor_catchments[i], donor_catchments[j])
        return sigma

    def _matrix_sigma_eps(self, donor_catchments):
        """
        Return sampling error coveriance matrix Sigma eta

        Methodology source: Kjeldsen & Jones 2009, eq 9

        :param donor_catchments: Catchments to use as donors
        :type donor_catchments: list of :class:`Catchment`
        :return: 2-Dimensional, symmetric covariance matrix
        :rtype: :class:`numpy.ndarray`
        """
        p = len(donor_catchments)
        sigma = np.empty((p, p))
        for i in range(p):
            beta_i = self._beta(donor_catchments[i])
            n_i = donor_catchments[i].amax_records_end() - donor_catchments[i].amax_records_start() + 1
            for j in range(p):
                beta_j = self._beta(donor_catchments[j])
                n_j = donor_catchments[j].amax_records_end() - donor_catchments[j].amax_records_start() + 1
                rho_ij = self._lnqmed_corr(donor_catchments[i], donor_catchments[j])
                n_ij = min(donor_catchments[i].amax_records_end(), donor_catchments[j].amax_records_end()) - \
                       max(donor_catchments[i].amax_records_start(), donor_catchments[j].amax_records_start()) + 1
                sigma[i, j] = 4 * beta_i * beta_j * n_ij / n_i / n_j * rho_ij
        return sigma

    def _matrix_omega(self, donor_catchments):
        return self._matrix_sigma_eta(donor_catchments) + self._matrix_sigma_eps(donor_catchments)

    def _vec_alpha(self, donor_catchments):
        """
        Return vector alpha which is the weights for donor model errors

        Methodology source: Kjeldsen, Jones & Morris 2014, eq 10

        :param donor_catchments: Catchments to use as donors
        :type donor_catchments: list of :class:`Catchment`
        :return: Vector of donor weights
        :rtype: :class:`numpy.ndarray`
        """
        return np.dot(linalg.inv(self._matrix_omega(donor_catchments)), self._vec_b(donor_catchments))

    @staticmethod
    def _lnqmed_residual(catchment):
        """
        Return ln(QMED) model error at a gauged catchment

        :param catchment: Gauged catchment
        :type catchment: :class:`Catchment`
        :return: Model error
        :rtype: float
        """
        analysis = QmedAnalysis(catchment, year=2000)  # Probably should set the year to the midpoint of amax rec.
        logmedian_amax = log(analysis.qmed(method='amax_records'))
        logmedian_descr = log(analysis.qmed(method='descriptors'))
        return logmedian_amax - logmedian_descr

    def _vec_lnqmed_residuals(self, catchments):
        """
        Return ln(QMED) model errors for a list of catchments

        :param catchments: List of gauged catchments
        :type catchments: list of :class:`Catchment`
        :return: Model errors
        :rtype: list of float
        """
        result = np.empty(len(catchments))
        for index, donor in enumerate(catchments):
            result[index] = self._lnqmed_residual(donor)
        return result

    def find_donor_catchments(self, limit=6, dist_limit=500):
        """
        Return a suitable donor catchment to improve a QMED estimate based on catchment descriptors alone.

        :param limit: maximum number of catchments to return. Default: 20. Set to `None` to return all available
                      catchments.
        :type limit: int
        :param dist_limit: maximum distance in km. between subject and donor catchment. Default: 500 km. Increasing the
                           maximum distance will increase computation time!
        :type dist_limit: float or int
        :return: list of nearby catchments
        :rtype: :class:`floodestimation.entities.Catchment`
        """
        if self.gauged_catchments:
            return self.gauged_catchments.nearest_qmed_catchments(self.catchment, limit, dist_limit)
        else:
            return []


class GrowthCurveAnalysis(Analysis):
    """
    Class to undertake a growth curve analysis.
    """

    #: Methods available to estimate the growth curve
    methods = ('enhanced_single_site', 'single_site', 'pooling_group')
    #: Available distribution functions for growth curves
    distributions = ('glo', 'gev')

    def __init__(self, catchment, gauged_catchments=None, year=None, results_log=None):
        """
        :param catchment: subject catchment
        :type catchment: :class:`.entities.Catchment`
        :param gauged_catchments: catchment collections objects for retrieval of gauged data for donor analyses
        :type gauged_catchments: :class:`.collections.CatchmentCollections`
        """
        Analysis.__init__(self, year, results_log)

        self.catchment = catchment
        self.gauged_cachments = gauged_catchments

        #: List of donor catchments. Either set manually or by calling
        #: :meth:`.GrowthCurveAnalysis.find_donor_catchments` or implicitly when calling :meth:`.growth_curve()`.
        self.donor_catchments = []

    def growth_curve(self, method='best', **method_options):
        """
        Return QMED estimate using best available methodology depending on what catchment attributes are available.

        ====================== ====================== ==================================================================
        `method`               `method_options`       notes
        ====================== ====================== ==================================================================
        `enhanced_single_site` `distr='glo'`          Preferred method for gauged catchments (i.e. with
                               `as_rural=False`       `Catchment.amax_record`).
        `single_site`          `distr='glo'`          Alternative method for gauged catchments. Uses AMAX data from
                                                      subject station only.
        `pooling_group`        `distr='glo'`          Only possible method for ungauged catchments.
                               `as_rural=False`
        ====================== ====================== ==================================================================

        :param method: methodology to use to estimate the growth curve. Default: automatically choose best method.
        :type method: str
        :param method_options: any optional parameters for the growth curve method function
        :type method_options: kwargs
        :return: Inverse cumulative distribution function, callable class with one parameter `aep` (annual exceedance
                 probability)
        :type: :class:`.GrowthCurve`
        """
        if method == 'best':
            if self.catchment.amax_records:
                # Gauged catchment, use enhanced single site
                self.results_log['method'] = 'enhanced_single_site'
                return self._growth_curve_enhanced_single_site()
            else:
                # Ungauged catchment, standard pooling group
                self.results_log['method'] = 'pooling_group'
                return self._growth_curve_pooling_group()
        else:
            try:
                self.results_log['method'] = 'method'
                return getattr(self, '_growth_curve_' + method)(**method_options)
            except AttributeError:
                raise AttributeError("Method `{}` to estimate the growth curve does not exist.".format(method))

    @staticmethod
    def _dimensionless_flows(catchment):
        """
        Return array of flows devided by QMED

        :param catchment: gauged catchment with amax_records set
        :type catchment: :class:`floodestimation.entities.Catchment`
        :return: 1D array of flow values devided by QMED
        :rtype: :class:`numpy.ndarray`
        """
        flows = valid_flows_array(catchment)
        return flows / np.median(flows)

    def _var_and_skew(self, catchments, as_rural=False):
        """
        Calculate L-CV and L-SKEW from a single catchment or a pooled group of catchments.

        Methodology source: Science Report SC050050, para. 6.4.1-6.4.2
        """
        if not hasattr(catchments, '__getitem__'):  # In case of a single catchment
            l_cv, l_skew = self._l_cv_and_skew(self.catchment)
            self.results_log['donors'] = []
        else:
            # Prepare arrays for donor L-CVs and L-SKEWs and their weights
            n = len(catchments)
            l_cvs = np.empty(n)
            l_skews = np.empty(n)
            l_cv_weights = np.empty(n)
            l_skew_weights = np.empty(n)

            # Fill arrays
            for index, donor in enumerate(catchments):
                l_cvs[index], l_skews[index] = self._l_cv_and_skew(donor)
                l_cv_weights[index] = self._l_cv_weight(donor)
                l_skew_weights[index] = self._l_skew_weight(donor)

            # Weighted averages of L-CV and l-SKEW
            l_cv_weights /= sum(l_cv_weights)  # Weights sum to 1
            # Special case if the first donor is the subject catchment itself, assumed if similarity distance == 0.
            if self._similarity_distance(self.catchment, catchments[0]) == 0:
                l_cv_weights *= self._l_cv_weight_factor()  # Reduce weights of all donor catchments
                l_cv_weights[0] += 1 - sum(l_cv_weights)    # But increase the weight of the subject catchment
            l_cv_rural = sum(l_cv_weights * l_cvs)
            l_skew_weights /= sum(l_skew_weights)  # Weights sum to 1
            l_skew_rural = sum(l_skew_weights * l_skews)
            self.results_log['l_cv_rural'] = l_cv_rural
            self.results_log['l_skew_rural'] = l_skew_rural

            if as_rural:
                l_cv = l_cv_rural
                l_skew = l_skew_rural
            else:
                # Method source: eqns. 10 and 11, Kjeldsen 2010
                l_cv = l_cv_rural * 0.5547 ** self.catchment.descriptors.urbext(self.year)
                l_skew = (l_skew_rural + 1) * 1.1545 ** self.catchment.descriptors.urbext(self.year) - 1

            # Record intermediate results (donors)
            self.results_log['donors'] = catchments
            total_record_length = 0
            for index, donor in enumerate(self.results_log['donors']):
                donor.l_cv = l_cvs[index]
                donor.l_cv_weight = l_cv_weights[index]
                donor.l_skew = l_skews[index]
                donor.l_skew_weight = l_skew_weights[index]
                donor.record_length = len(donor.amax_records)
                total_record_length += donor.record_length
            self.results_log['donors_record_length'] = total_record_length

        # Record intermediate results
        self.results_log['l_cv'] = l_cv
        self.results_log['l_skew'] = l_skew
        return l_cv, l_skew

    def _l_cv_and_skew(self, catchment):
        """
        Calculate L-CV and L-SKEW for a gauged catchment. Uses `lmoments3` library.

        Methodology source: Science Report SC050050, para. 6.7.5
        """
        z = self._dimensionless_flows(catchment)
        l1, l2, t3 = lm.lmom_ratios(z, nmom=3)
        return l2 / l1, t3

    def _l_cv_weight(self, donor_catchment):
        """
        Return L-CV weighting for a donor catchment.

        Methodology source: Science Report SC050050, eqn. 6.18 and 6.22a
        """
        try:
            dist = donor_catchment.similarity_dist
        except AttributeError:
            dist = self._similarity_distance(self.catchment, donor_catchment)
        b = 0.0047 * sqrt(dist) + 0.0023 / 2
        c = 0.02609 / (len(donor_catchment.amax_records) - 1)
        return 1 / (b + c)

    def _l_cv_weight_factor(self):
        """
        Return multiplier for L-CV weightings in case of enhanced single site analysis.

        Methodology source: Science Report SC050050, eqn. 6.15a and 6.15b
        """
        b = 0.0047 * sqrt(0) + 0.0023 / 2
        c = 0.02609 / (len(self.catchment.amax_records) - 1)
        return c / (b + c)

    def _l_skew_weight(self, donor_catchment):
        """
        Return L-SKEW weighting for donor catchment.

        Methodology source: Science Report SC050050, eqn. 6.19 and 6.22b
        """
        try:
            dist = donor_catchment.similarity_dist
        except AttributeError:
            dist = self._similarity_distance(self.catchment, donor_catchment)
        b = 0.0219 * (1 - exp(-dist / 0.2360))
        c = 0.2743 / (len(donor_catchment.amax_records) - 2)
        return 1 / (b + c)

    def _growth_curve_single_site(self, distr='glo'):
        """
        Return flood growth curve function based on `amax_records` from the subject catchment only.

        :return: Inverse cumulative distribution function with one parameter `aep` (annual exceedance probability)
        :type: :class:`.GrowthCurve`
        """
        if self.catchment.amax_records:
            self.donor_catchments = []
            return GrowthCurve(distr, *self._var_and_skew(self.catchment))
        else:
            raise InsufficientDataError("Catchment's `amax_records` must be set for a single site analysis.")

    def _growth_curve_pooling_group(self, distr='glo', as_rural=False):
        """
        Return flood growth curve function based on `amax_records` from a pooling group.

        :return: Inverse cumulative distribution function with one parameter `aep` (annual exceedance probability)
        :type: :class:`.GrowthCurve`
        :param as_rural: assume catchment is fully rural. Default: false.
        :type as rural: bool
        """
        if not self.donor_catchments:
            self.find_donor_catchments()
        gc = GrowthCurve(distr, *self._var_and_skew(self.donor_catchments))

        # Record intermediate results
        self.results_log['distr_name'] = distr.upper()
        self.results_log['distr_params'] = gc.params
        return gc

    def _growth_curve_enhanced_single_site(self, distr='glo', as_rural=False):
        """
        Return flood growth curve function based on `amax_records` from the subject catchment and a pooling group.

        :return: Inverse cumulative distribution function with one parameter `aep` (annual exceedance probability)
        :type: :class:`.GrowthCurve`
        :param as_rural: assume catchment is fully rural. Default: false.
        :type as rural: bool
        """
        if not self.donor_catchments:
            self.find_donor_catchments(include_subject_catchment='force')
        gc =  GrowthCurve(distr, *self._var_and_skew(self.donor_catchments))

        # Record intermediate results
        self.results_log['distr_name'] = distr.upper()
        self.results_log['distr_params'] = gc.params
        return gc

    #: Dict of weighting factors and standard deviation for catchment descriptors to use in calculating the similarity
    #: distance measure between the subject catchment and each donor catchment. The dict is structured like this:
    #: `{parameter: (weight, standard deviation, transform method)}`. The transform method is optional and is typically
    #: omitted or set to `log`.
    # TODO: calculate standard deviation from database
    similarity_params = {'dtm_area': (3.2, 1.28, log),  # param: (weight, std_dev, transform method)
                         'saar': (0.5, 0.37, log),
                         'farl': (0.1, 0.05),
                         'fpext': (0.2, 0.04)}

    def _similarity_distance(self, subject_catchment, other_catchment):
        dist_sq = 0
        for param, value in self.similarity_params.items():
            try:
                weight = value[0]
                std_dev = value[1]
                try:
                    transform = value[2]  # A method!
                except IndexError:
                    # If no transform method, just use linear
                    transform = lambda x: x
                dist_sq += weight * ((transform(getattr(other_catchment.descriptors, param))
                                      - transform(getattr(subject_catchment.descriptors, param))) / std_dev) ** 2
            except TypeError:
                # If either of the catchments do not have the descriptor, assume infinitely large distance
                dist_sq += float('inf')
        return sqrt(dist_sq)

    def find_donor_catchments(self, include_subject_catchment='auto'):
        """
        Find list of suitable donor cachments, ranked by hydrological similarity distance measure. This method is
        implicitly called when calling the :meth:`.growth_curve` method unless the attribute :attr:`.donor_catchments`
        is set manually.

        The results are stored in :attr:`.donor_catchments`. The (list of)
        :class:`floodestimation.entities.Catchment` will have an additional attribute :attr:`similarity_dist`.

        :param include_subject_catchment: - `auto`: include subject catchment if suitable for pooling and if urbext2000
                                            < 0.03
                                          - `force`: always include subject catchment
                                          - `exclude`: do not include the subject catchment
        :type include_subject_catchment: str
        """

        # Only if we have access to db with gauged catchment data
        if self.gauged_cachments:
            self.donor_catchments = self.gauged_cachments. \
                most_similar_catchments(subject_catchment=self.catchment,
                                        similarity_dist_function=lambda c1, c2: self._similarity_distance(c1, c2),
                                        include_subject_catchment=include_subject_catchment)
        else:
            self.donor_catchments = []


class GrowthCurve():
    """
    Growth curve constructed using **sample** L-VAR and L-SKEW.

    The `GrowthCurve` class is callable, i.e. it can be used as a function. It has one parameter `aep`, which is an
    annual exceedance probability and can be either a single value or a list of values. In the latter case, a numpy
    :class:`ndarray` is returned.

    Example:

    >>> from floodestimation.analysis import GrowthCurve
    >>> growth_curve = GrowthCurve(distr='glo', var=0.2, skew=-0.1, kurtosis=0.185)
    >>> growth_curve(aep=0.5)
    1.0
    >>> growth_curve(aep=[0.1, 0.01, 0.001])
    array([ 1.38805928,  1.72475593,  1.98119739])
    >>> growth_curve.params
    [1.0, 0.1967263286166932, 0.1]
    >>> growth_curve.distr_kurtosis
    0.175
    >>> growth_curve.kurtosis_fit()
    0.010000000000000009

    """
    def __init__(self, distr, var, skew, kurtosis=None):
        #: Statistical distribution function abbreviation, e.g. 'glo', 'gev'. Any supported by the :mod:`lmoments3`
        #: package can be used.
        self.distr = distr
        #: Sample L-variance (t2)
        self.var = var
        #: Sample L-skew (t3)
        self.skew = skew
        #: Sample L-kurtosis (t4, not used to create distribution function)
        self.kurtosis = kurtosis
        try:
            #: Statistical distribution as scipy `rv_continous` class, extended with L-moment methods.
            self.distr_f = getattr(lm_distr, distr)
            #: Distribution function parameter. Except for the `loc` parameter, all other parameters are estimated using
            #: the sample variance and skew linear moments.
            self.params = self.distr_f.lmom_fit(lmom_ratios=[1, var, skew])
            self.params['loc'] = self._solve_location_param()

            #: The **distribution's** L-kurtosis which may be different from the **sample** L-kurtosis (t4).
            self.distr_kurtosis = self.distr_f.lmom_ratios(nmom=4, **self.params)[3]
        except AttributeError:
            raise InsufficientDataError("Distribution function `{}` does not exist.".format(distr))

    def __call__(self, aep):
        return self.distr_f.ppf(1 - np.array(aep), **self.params)

    def _solve_location_param(self):
        """
        We're lazy here and simply iterate to find the location parameter such that growth_curve(0.5)=1.
        """
        params = copy.copy(self.params)
        del params['loc']

        f = lambda location: self.distr_f.ppf(0.5, loc=location, **params) - 1
        return optimize.brentq(f, -10, 10)

    def kurtosis_fit(self):
        """
        Estimate the goodness of fit by calculating the difference between sample L-kurtosis and distribution function
        L-kurtosis.

        :return: Goodness of fit measure
        :rtype: float
        """
        try:
            return self.kurtosis - self.distr_kurtosis
        except TypeError:
            raise InsufficientDataError("The (sample) L-kurtosis must be set before the fit can be calculated.")


class InsufficientDataError(BaseException):
    pass