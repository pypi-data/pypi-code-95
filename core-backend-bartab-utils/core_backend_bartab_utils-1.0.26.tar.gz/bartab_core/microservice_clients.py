from rest_framework.exceptions import APIException
from .microservices import AbstractMicroservice
from .cache_manager import CacheManager


class PainkillerUnavailable(APIException):
    status_code = 503
    default_detail = 'Order service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class GreatPumpkinUnavailable(APIException):
    status_code = 503
    default_detail = 'Payment service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class CementMixerUnavailable(APIException):
    status_code = 503
    default_detail = 'Location service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'

class PainkillerClient(AbstractMicroservice):

    def __init__(self):
        super().__init__(
            url_prefix="pain",
            localhost_port="7777",
            service_name='painkiller',
            exception=PainkillerUnavailable,
            api_version="v1",
            service_description='order manager'
            )


class GreatPumpkinClient(AbstractMicroservice):
    def __init__(self):
        super().__init__(
            url_prefix="pumpkin",
            localhost_port="2344",
            service_name='great-pumpkin',
            exception=GreatPumpkinUnavailable,
            api_version="v1",
            service_description='payment manager'
        )


class CementMixerClient(AbstractMicroservice):


    class CementMixerCacheManager:
        LOCATION_INFO_BY_LOCATION_ID_KEY_NAME = 'location_info_by_location_id_map'

        def __init__(self):
            self.cache_manager = CacheManager.get_instance()

        def get_location_info_or_none(self, location_id: str) -> dict:
            location_info_by_location_id_map = self.cache_manager.set_or_get(
            self.LOCATION_INFO_BY_LOCATION_ID_KEY_NAME, {})

            return None if location_id not in location_info_by_location_id_map else location_info_by_location_id_map[location_id]

        def set_location_info(self, location_info: dict):
            location_info_by_location_id_map = self.cache_manager.set_or_get(
                self.LOCATION_INFO_BY_LOCATION_ID_KEY_NAME, {})
            
            location_info_by_location_id_map[location_info['uuid']] = location_info

            self.cache_manager.set(
                self.LOCATION_INFO_BY_LOCATION_ID_KEY_NAME, location_info_by_location_id_map
            )


    def __init__(self):
        super().__init__(
            url_prefix="api",
            localhost_port="8000",
            service_name='cement-mixer',
            exception=CementMixerUnavailable,
            api_version="v1",
            service_description='location manager'
        )

        self.cache_manager = self.CementMixerCacheManager()



    def get_location_info(self, location_id: str, use_cache: bool = True) -> str:
        if use_cache:
            location_info = self.cache_manager.get_location_info_or_none(location_id)

            if location_info != None:
                return location_info

        location_info = self.get(f"location/{location_id}").json()

        self.cache_manager.set_location_info(location_info)

        return location_info



        

