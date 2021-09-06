# -*- coding: utf-8 -*-

""" ddsctrl/constants.py """

ORGANIZATION = "FEMTO_Engineering"
APP_NAME = "ddscontroller"
APP_BRIEF = "GUI dedicated to handle AD9912 and AD9915 DDS board device"
AUTHOR_NAME = "Benoit Dubois"
AUTHOR_MAIL = "benoit.dubois@femto-engineering.fr"
COPYRIGHT = "FEMTO ENGINEERING, 2016, 2021"
LICENSE = "GNU GPL v3.0 or upper."

DEFAULT_AUTO_UPDATE = False   # Default automatic update state

AD9912_VCO_RANGE = {0: "700 MHz to 810 MHz", 1: "900MHz to 1000 MHz", 2: "Automatic"}
AD9912_CP_CURRENT = {0: "250 µA", 1: "375 µA", 2:"Off", 3: "125 µA"}
DEFAULT_AD9912_IFREQ = 1000000000.0  # Default DDS input frequency
DEFAULT_AD9912_OFREQ = 10000000.0    # Default DDS output frequency
DEFAULT_AD9912_AMP = 511             # Default DDS output amplitude (between 0 to 1023)
DEFAULT_AD9912_PHASE = 0             # Default DDS phase
DEFAULT_AD9912_PLL_EN = False        # Default PLL enable state
DEFAULT_AD9912_PLL_DOUBLER = False   # Default PLL doubler state
DEFAULT_AD9912_PLL_FACTOR = 4        # Default PLL multiplication factor
DEFAULT_AD9912_CP_CURRENT = 2        # Default CP current index (see AD9912_CP_CURRENT dict)
DEFAULT_AD9912_VCO_RANGE = 2         # Default VCO range index (see AD9912_VCO_RANGE dict)
DEFAULT_AD9912_HSTL_EN = False       # Default HSTL enable state
DEFAULT_AD9912_CMOS_EN = False       # Default CMOS enable state
DEFAULT_AD9912_HSTL_DOUBLER = False  # Default HSTL doubler state

DEFAULT_AD9915_IFREQ = 2500000000.0  # Default DDS input frequency
DEFAULT_AD9915_OFREQ = 1000000000.0  # Default DDS output frequency
DEFAULT_AD9915_AMP = 511             # Default DDS output amplitude (between 0 to 1023)
