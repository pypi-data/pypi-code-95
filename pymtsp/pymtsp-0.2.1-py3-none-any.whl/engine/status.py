from enum import Enum


class DepotStatus(Enum):
    IDLE = 0  # serves as type place holder for depot


class CityStatus(Enum):
    IDLE = 1  # Not visited/assigned to a salesman
    ASSIGNED = 2  # assigned to some salesman; the assigned salesmen is about to leave the tour/ or on the tour
    INACTIVE = 3  # already visited


class SalesmanStatus(Enum):
    IDLE = 4  # ready to be assigned
    ASSIGNED = 5  # on a "traveling"
    INACTIVE = 6  # already return to the depot

