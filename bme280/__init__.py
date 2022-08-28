#
# BME280 device driver - Public interface
# Copyright (c) 2020-2022 Michael Büsch <m@bues.ch>
#
# The reference and base for this software is the public document
#   BME280 - Data sheet
#   Document revision         1.6
#   Document release date     September 2018
#   Technical reference code  0 273 141 185
#   Document number           BST-BME280-DS002-15
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__all__ = [
    "BME280", "BME280Error",
    "MODE_SLEEP", "MODE_FORCED", "MODE_NORMAL",
    "OVSMPL_SKIP", "OVSMPL_1", "OVSMPL_2", "OVSMPL_4", "OVSMPL_8", "OVSMPL_16",
    "T_SB_p5ms", "T_SB_10ms", "T_SB_20ms", "T_SB_62p5ms", "T_SB_125ms", "T_SB_250ms", "T_SB_500ms", "T_SB_1000ms",
    "FILTER_OFF", "FILTER_2", "FILTER_4", "FILTER_8", "FILTER_16",
    "CALC_FLOAT", "CALC_INT32", "CALC_INT64",
]

# Export public classes
from .bme280 import BME280, BME280Error
# Export public constants
from .bme280 import MODE_SLEEP, MODE_FORCED, MODE_NORMAL
from .bme280 import OVSMPL_SKIP, OVSMPL_1, OVSMPL_2, OVSMPL_4, OVSMPL_8, OVSMPL_16
from .bme280 import T_SB_p5ms, T_SB_10ms, T_SB_20ms, T_SB_62p5ms, T_SB_125ms, T_SB_250ms, T_SB_500ms, T_SB_1000ms
from .bme280 import FILTER_OFF, FILTER_2, FILTER_4, FILTER_8, FILTER_16
from .bme280 import CALC_FLOAT, CALC_INT32, CALC_INT64

# vim: ts=4 sw=4 expandtab
