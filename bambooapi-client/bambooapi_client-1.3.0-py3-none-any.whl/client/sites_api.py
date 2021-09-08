"""Sites are physical locations where flexibility devices are deployed."""
import typing as tp

from bambooapi_client.api.sites_api import SitesApi as _SitesApi
from bambooapi_client.exceptions import NotFoundException
from bambooapi_client.model.activation_state import ActivationState
from bambooapi_client.model.baseline_model import BaselineModel
from bambooapi_client.model.flexibility_model import FlexibilityModel
from bambooapi_client.model.site import Site
from bambooapi_client.model.site_data_point import SiteDataPoint
from bambooapi_client.model.site_list_item import SiteListItem
from bambooapi_client.model.thermal_zone import ThermalZone

import pandas as pd


class SitesApi(object):
    """Implementation for '/v1/sites' endpoints."""

    def __init__(self, bambooapi_client):
        """Initialize defaults."""
        self._bambooapi_client = bambooapi_client
        self._api_instance = _SitesApi(bambooapi_client.api_client)

    def list_sites(self) -> tp.List[SiteListItem]:
        """List sites."""
        return self._api_instance.list_sites(_check_return_type=False)

    def get_site(self, site_id: int) -> tp.Optional[Site]:
        """Get site by id."""
        try:
            return self._api_instance.read_site(site_id, _check_return_type=False)
        except NotFoundException:
            return None

    def get_site_id(self, site_name: str) -> tp.Optional[int]:
        """Get site id by name."""
        try:
            return self._api_instance.get_site_id_by_name(site_name)
        except NotFoundException:
            return None

    def list_devices(
        self,
        site_id: int,
        device_type: str = 'hvac',
    ) -> tp.List[tp.Any]:
        """List devices for a given site."""
        return self._api_instance.list_devices(
            site_id,
            device_type=device_type,
            _check_return_type=False,
        )

    def get_device(self, site_id: int, device_name: str) -> tp.Optional[dict]:
        """Get single device by name for a given site."""
        try:
            return self._api_instance.read_device(site_id, device_name)
        except NotFoundException:
            return None

    def list_zones(self, site_id: int) -> tp.List[ThermalZone]:
        """List zones for a given site."""
        return self._api_instance.list_zones(site_id)

    def get_zone(
        self,
        site_id: int,
        zone_name: str,
    ) -> tp.Optional[ThermalZone]:
        """Get single zone by name for a given site."""
        try:
            return self._api_instance.read_zone(site_id, zone_name)
        except NotFoundException:
            return None

    def read_baseline_model(
        self,
        site_id: int,
        device_name: str,
        horizon: str = 'day-ahead',
    ) -> tp.Optional[BaselineModel]:
        """Read baseline model for a given site and device."""
        try:
            return self._api_instance.read_baseline_model(site_id, device_name,
                                                          horizon=horizon,
                                                          _check_return_type=False)
        except NotFoundException:
            return None

    def update_baseline_model(
        self,
        site_id: int,
        device_name: str,
        baseline_model: tp.Union[BaselineModel, dict],
        horizon: str = 'day-ahead',
    ) -> BaselineModel:
        """Update baseline model for a given site and device."""
        return self._api_instance.update_baseline_model(site_id, device_name,
                                                        baseline_model,
                                                        horizon=horizon)

    def read_measurements(
        self,
        site_id: int,
        device_name: int,
        start: tp.Optional[str] = None,
        stop: tp.Optional[str] = None,
    ) -> tp.Optional[pd.DataFrame]:
        """Read site device measurements."""
        if start and stop:
            _meas = self._api_instance.read_device_measurements(
                site_id,
                device_name,
                period='CustomRange',
                period_start=start,
                period_stop=stop,
                _check_return_type=False,
            )
        else:
            _meas = self._api_instance.read_device_measurements(site_id, device_name)
        # Convert SiteDataPoint objects to dict before converting to DF
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            # Convert to DF
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_measurements(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
    ) -> tp.List[SiteDataPoint]:
        """Update site device measurements."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_device_measurements(
            site_id,
            device_name,
            _dps,
        )

    def read_forecasts(
        self,
        site_id: int,
        device_name: str,
        horizon: str = 'day-ahead',
        start: tp.Optional[str] = None,
        stop: tp.Optional[str] = None,
    ) -> tp.Optional[pd.DataFrame]:
        """Read site device forecasts."""
        if start and stop:
            _meas = self._api_instance.read_device_forecasts(
                site_id,
                device_name,
                horizon=horizon,
                period='CustomRange',
                period_start=start,
                period_stop=stop,
                _check_return_type=False,
            )
        else:
            _meas = self._api_instance.read_device_forecasts(
                site_id,
                device_name,
            )
        # Convert DataPoint objects to dict before converting to DF
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            # Convert to DF
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_forecasts(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
        horizon: str,
    ) -> tp.List[SiteDataPoint]:
        """Update site device forecasts."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_device_forecasts(
            site_id,
            device_name,
            _dps,
            horizon=horizon,
        )

    def read_activations(
        self,
        site_id: int,
        device_name: str,
    ) -> tp.Optional[ActivationState]:
        """Read site device activations."""
        try:
            return self._api_instance.read_device_activations(
                site_id,
                device_name,
                _check_return_type=False,
            )
        except NotFoundException:
            return None

    def read_flexibility_model(
        self,
        site_id: int,
        zone_name: str,
        horizon: str = 'day-ahead',
    ) -> tp.Optional[BaselineModel]:
        """Read thermal flexibility model for a given site and zone."""
        try:
            return self._api_instance.read_flexibility_model(
                site_id,
                zone_name,
                horizon=horizon,
                _check_return_type=False,
            )
        except NotFoundException:
            return None

    def update_flexibility_model(
        self,
        site_id: int,
        zone_name: str,
        flexibility_model: tp.Union[FlexibilityModel, dict],
        horizon: str = 'day-ahead',
    ) -> BaselineModel:
        """Update thermal flexibility model for a given site and zone."""
        return self._api_instance.update_flexibility_model(
            site_id,
            zone_name,
            flexibility_model,
            horizon=horizon,
        )
