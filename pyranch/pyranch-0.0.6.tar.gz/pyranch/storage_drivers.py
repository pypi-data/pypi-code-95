from .common import CattleObject
from .exceptions import RequestError


class StorageDriver(CattleObject):
    object_url = 'storagedrivers'

    def __init__(self, environment, storage_driver_id=None, storage_driver_name=None):
        self.env = environment
        if storage_driver_id:
            self.storage_driver_url = '{}/{}'.format(self.object_url, storage_driver_id)
            storage_driver_data = environment.request(self.storage_driver_url, 'GET')
        elif storage_driver_name:
            self.name = storage_driver_name
            storage_driver_data = self.find_by_name()
            if storage_driver_data:
                self.storage_driver_url = '{}/{}'.format(self.object_url, storage_driver_data.get('id'))
        else:
            # Create stack object for list fetch
            storage_driver_data = {}
        # Read only values
        self.id = storage_driver_data.get('id') or None
        self.type = storage_driver_data.get('type') or ''
        self.state = storage_driver_data.get('state') or None
        self.serviceId = storage_driver_data.get('serviceId') or None

        # Write values
        self.name = storage_driver_data.get('name') or {}
        self.blockDevicePath = storage_driver_data.get('blockDevicePath') or ''
        self.description = storage_driver_data.get('description') or None
        self.scope = storage_driver_data.get('scope') or None


    @property
    def get_metadata(self):
        if not self.id:
            raise RequestError
        json = {
            'id': self.id,
            'name': self.name,
            'url': self.env.endpoint + self.storage_driver_url,
            'state': self.state,
            'serviceId': self.serviceId,
            'type': self.type,
            'blockDevicePath': self.blockDevicePath,
            'description': self.description,
            'scope': self.scope
        }
        return json

    # Actions

    def update(self):
        return self.action('update')

    def remove(self):
        return self.action('remove')

    def deactivate(self):
        return self.action('deactivate')
