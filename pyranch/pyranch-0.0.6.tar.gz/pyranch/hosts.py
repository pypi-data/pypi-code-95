from .common import CattleObject
from .exceptions import RequestError


class Host(CattleObject):
    object_url = 'hosts'

    def __init__(self, environment, host_id=None, host_name=None):
        self.env = environment
        if host_id:
            self.host_url = '{}/{}'.format(self.object_url, host_id)
            host_data = environment.request(self.host_url, 'GET')
        elif host_name:
            self.name = host_name
            host_data = self.find_by_name()
            if host_data:
                self.host_url = '{}/{}'.format(self.object_url, host_data.get('id'))
        else:
            # Create host object for list fetch
            host_data = {}
        # Read only values
        self.state = host_data.get('state') or None
        self.id = host_data.get('id') or host_id
        self.name = host_data.get('name') or None
        # Write values
        self.hostname = host_data.get('hostname') or host_name

    @property
    def get_metadata(self):
        if not self.id:
            raise RequestError
        json = {
            'id': self.id,
            'name': self.name,
            'hostname': self.hostname,
            'url': self.env.endpoint + self.host_url,
            'state': self.state
        }
        return json

    def create(self):
        data = {
            'hostname': self.hostname
        }
        new_host = self.env.request(self.object_url, 'POST', data=data)
        self.state = new_host.get('state')
        self.id = new_host.get('id')
        self.host_url = '{}/{}'.format(self.object_url, self.id)

    def save(self):
        if not self.id:
            raise RequestError
        data = {
            'hostname': self.hostname,
        }
        self.env.request(self.host_url, 'PUT', data=data)

    # Actions

    def activate(self):
        return self.action('activate')

    def deactivate(self):
        return self.action('deactivate')

    def delete(self):
        return self.action('delete')

    def error(self):
        return self.action('error')

    def upgrade(self):
        data = {
            'hostname': self.hostname
        }
        self.action('upgrade', data=data)
