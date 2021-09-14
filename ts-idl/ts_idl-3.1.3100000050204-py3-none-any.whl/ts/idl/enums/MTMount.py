# This file is part of ts_idl.
#
# Developed for Vera Rubin Observatory.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
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

__all__ = ["DriveState"]

import enum


class AxisState(enum.IntEnum):
    """Axis state."""

    UNKNOWN = 0
    OFF = enum.auto()
    IDLE = enum.auto()
    ENABLED = enum.auto()
    DISCRETE_MOVE = enum.auto()
    JOG_MOVE = enum.auto()
    TRACKING = enum.auto()
    STOPPING = enum.auto()
    FAULT = enum.auto()


class DriveState(enum.IntEnum):
    """Drive state.

    Reported as statusDrive by the low-level controller.
    """

    UNKNOWN = 0
    OFF = enum.auto()
    MOVING = enum.auto()
    STOPPING = enum.auto()
    STOPPED = enum.auto()
    FAULT = enum.auto()


class SubsystemId(enum.IntEnum):
    AZIMUTH_AXIS = 100
    AZIMUTH_DRIVE = 200
    AZIMUTH_CABLE_WRAP = 300
    ELEVATION_AXIS = 400
    ELEVATION_DRIVE = 500
    MAIN_POWER_SUPPLY = 600
    ENCODER_INTERFACE_BOX = 700
    OIL_SUPPLY_SYSTEM = 800
    MIRROR_COVERS = 900
    CAMERA_CABLE_WRAP = 1000
    BALANCE = 1100
    DEPLOYABLE_PLATFORM = 1200
    CABINET = 1300
    LOCKING_PINS = 1400
    MIRROR_COVER_LOCKS = 1500
    AZIMUTH_THERMAL = 1600
    ELEVATION_THERMAL = 1700
    INTERLOCK = 1800
    TOP_END_CHILLER = 2200
