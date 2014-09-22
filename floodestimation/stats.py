# -*- coding: utf-8 -*-

# Copyright (c) 2014 and Florenz A.P. Hollebrandse <f.a.p.hollebrandse@protonmail.ch>
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
Module containing simple statistic functions
"""
from math import floor, ceil


def median(x):
    x_sorted = sorted(x)
    length = len(x)
    if length < 2:
        raise "List should have at least 2 items to calculate a median."
    return 0.5 * x_sorted[int(floor(0.5 * (length - 1)))] + 0.5 * x_sorted[int(ceil(0.5 * (length - 1)))]


def mean(x):
    return sum(x)/len(x)