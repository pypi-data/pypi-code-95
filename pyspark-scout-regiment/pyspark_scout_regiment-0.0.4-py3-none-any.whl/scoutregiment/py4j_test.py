from scoutregiment import *
import py4j

option.scout_member_pattern = \
"""

^[^A-Z_]+$

"""
option.scout_depth_max = 1
option.scout_leader = ScoutOption._levi


