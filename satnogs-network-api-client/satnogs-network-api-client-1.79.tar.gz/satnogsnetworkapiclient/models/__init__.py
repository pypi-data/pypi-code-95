# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from satnogsnetworkapiclient.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from satnogsnetworkapiclient.model.demod_data import DemodData
from satnogsnetworkapiclient.model.job import Job
from satnogsnetworkapiclient.model.new_observation import NewObservation
from satnogsnetworkapiclient.model.observation import Observation
from satnogsnetworkapiclient.model.paginated_observation_list import PaginatedObservationList
from satnogsnetworkapiclient.model.paginated_station_list import PaginatedStationList
from satnogsnetworkapiclient.model.paginated_transmitter_list import PaginatedTransmitterList
from satnogsnetworkapiclient.model.patched_observation import PatchedObservation
from satnogsnetworkapiclient.model.station import Station
from satnogsnetworkapiclient.model.transmitter import Transmitter
from satnogsnetworkapiclient.model.transmitter_type_enum import TransmitterTypeEnum
