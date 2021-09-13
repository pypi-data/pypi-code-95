from .common import CattleObject
from .exceptions import RequestError


class Volume(CattleObject):
    object_url = 'volumes'

    def __init__(self, environment, volume_id=None, volume_name=None):
        self.env = environment
        if volume_id:
            self.volume_url = '{}/{}'.format(self.object_url, volume_id)
            volume_data = environment.request(self.volume_url, 'GET')
        elif volume_name:
            self.name = volume_name
            volume_data = self.find_by_name()
            if volume_data:
                self.volume_url = '{}/{}'.format(self.object_url, volume_data.get('id'))
        else:
            # Create stack object for list fetch
            volume_data = {}

        # Read only values
        self.id = volume_data.get('id') or None
        self.state = volume_data.get('state') or None

        # Write values
        self.name = volume_data.get('name') or volume_name
        self.description = volume_data.get('description') or None
        self.storageDriverId = volume_data.get('storageDriverId') or None
        self.driver = volume_data.get('driver') or None
        self.driverOpts = volume_data.get('driverOpts') or {}
        self.externalId = volume_data.get('externalId') or None
        self.hostId = volume_data.get('hostId') or None
        self.imageId = volume_data.get('imageId') or None
        self.instanceId = volume_data.get('instanceId') or None
        self.stackId = volume_data.get('stackId') or None
        self.sizeMb = volume_data.get('sizeMb') or None
        self.volumeTemplateId = volume_data.get('volumeTemplateId') or None

    @property
    def get_metadata(self):
        if not self.id:
            raise RequestError
        json = {
            'id': self.id,
            'name': self.name,
            'url': self.env.endpoint + self.volume_url,
            'state': self.state,
            'description': self.description,
            'storageDriverId': self.storageDriverId,
            'driver': self.driver,
            'driverOpts': self.driverOpts,
            'externalId': self.externalId,
            'hostId': self.hostId,
            'imageId': self.imageId,
            'instanceId': self.instanceId,
            'stackId': self.stackId
        }
        return json

    def create(self):
        data = {
            'name': self.name,
            'description': self.description,
            'hostId': self.hostId,
            'storageDriverId': self.storageDriverId,
            'driver': self.driver,
            'driverOpts': self.driverOpts,
            'externalId': self.externalId,
            'imageId': self.imageId,
            'instanceId': self.instanceId,
            'stackId': self.stackId,
            'sizeMb': self.sizeMb,
            'volumeTemplateId': self.volumeTemplateId
        }
        new_volume = self.env.request(self.object_url, 'POST', data=data)
        self.state = new_volume.get('state')
        self.id = new_volume.get('id')
        self.volume_url = '{}/{}'.format(self.object_url, self.id)

    def save(self):
        if not self.id:
            raise RequestError
        data = {
            'name': self.name,
            'description': self.description,
            'hostId': self.hostId,
            'storageDriverId': self.storageDriverId,
            'driver': self.driver,
            'driverOpts': self.driverOpts,
            'externalId': self.externalId,
            'imageId': self.imageId,
            'instanceId': self.instanceId,
            'stackId': self.stackId,
            'sizeMb': self.sizeMb,
            'volumeTemplateId': self.volumeTemplateId
        }
        self.env.request(self.volume_url, 'PUT', data=data)

    # Actions

    def allocate(self):
        return self.action('allocate')

    def deallocate(self):
        return self.action('deallocate')

    def update(self):
        return self.action('update')

    def purge(self):
        return self.action('purge')

    def remove(self):
        return self.action('remove')

    def restorefrombackup(self):
        return self.action('restorefrombackup')

    def reverttosnapshot(self):
        return self.action('reverttosnapshot')

    def snapshot(self):
        return self.action('snapshot')