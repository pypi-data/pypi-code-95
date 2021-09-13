from .common import CattleObject
from .exceptions import RequestError


class Service(CattleObject):
    object_url = 'services'

    def __init__(self, environment, service_id=None, service_name=None):
        self.env = environment
        if service_id:
            self.service_url = '{}/{}'.format(self.object_url, service_id)
            service_data = environment.request(self.service_url, 'GET')
        elif service_name:
            self.name = service_name
            service_data = self.find_by_name()
            if service_data:
                self.service_url = '{}/{}'.format(self.object_url, service_data.get('id'))
        else:
            # Create service object for list fetch
            service_data = {}

        # Read only values
        self.state = service_data.get('state') or None
        self.healthState = service_data.get('healthState') or None
        self.id = service_data.get('id') or None
        self.instanceIds = service_data.get('instanceIds') or []
        self.system = service_data.get('system') or False
        self.createIndex = service_data.get('createIndex') or None
        self.currentScale = service_data.get('currentScale') or None
        self.fqdn = service_data.get('fqdn') or None
        self.linkedServices = service_data.get('linkedServices') or {}
        self.publicEndpoints = service_data.get('publicEndpoints') or []
        self.upgrade = service_data.get('upgrade') or {}
        # Write values
        self.assignServiceIpAddress = service_data.get('assignServiceIpAddress') or False
        self.description = service_data.get('description') or None
        self.externalId = service_data.get('externalId') or None
        self.launchConfig = service_data.get('launchConfig') or {}
        self.lbConfig = service_data.get('lbConfig') or {}
        self.metadata = service_data.get('metadata') or {}
        self.name = service_data.get('name') or service_name
        self.retainIp = service_data.get('retainIp') or False
        self.scale = service_data.get('scale') or 1
        self.scalePolicy = service_data.get('scalePolicy') or {}
        self.secondaryLaunchConfigs = service_data.get('secondaryLaunchConfigs') or []
        self.selectorContainer = service_data.get('selectorContainer') or None
        self.selectorLink = service_data.get('selectorLink') or None
        self.stackId = service_data.get('stackId') or {}
        self.startOnCreate = service_data.get('startOnCreate') or False
        self.vip = service_data.get('vip') or None

    @property
    def get_metadata(self):
        if not self.id:
            raise RequestError
        json = {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'healthState': self.healthState,
            'instanceIds': self.instanceIds,
            'system': self.system,
            'createIndex': self.createIndex,
            'currentScale': self.currentScale,
            'fqdn': self.fqdn,
            'linkedServices': self.linkedServices,
            'publicEndpoints': self.publicEndpoints,
            'upgrade': self.upgrade,
            'assignServiceIpAddress': self.assignServiceIpAddress,
            'description': self.description,
            'externalId': self.externalId,
            'launchConfig': self.launchConfig,
            'lbConfig': self.lbConfig,
            'metadata': self.metadata,
            'retainIp': self.retainIp,
            'scale': self.scale,
            'scalePolicy': self.scalePolicy,
            'secondaryLaunchConfigs': self.secondaryLaunchConfigs,
            'selectorContainer': self.selectorContainer,
            'selectorLink': self.selectorLink,
            'stackId': self.stackId,
            'startOnCreate': self.startOnCreate,
            'vip': self.vip,
        }
        return json

    def create(self):
        data = {
            'assignServiceIpAddress': self.assignServiceIpAddress,
            'description': self.description,
            'externalId': self.externalId,
            'launchConfig': self.launchConfig,
            'lbConfig': self.lbConfig,
            'metadata': self.metadata,
            'name': self.name,
            'retainIp': self.retainIp,
            'scale': self.scale,
            'scalePolicy': self.scalePolicy,
            'secondaryLaunchConfigs': self.secondaryLaunchConfigs,
            'selectorContainer': self.selectorContainer,
            'selectorLink': self.selectorLink,
            'stackId': self.stackId,
            'startOnCreate': self.startOnCreate,
            'vip': self.vip,
        }
        new_stack = self.env.request(self.object_url, 'POST', data=data)
        self.state = new_stack.get('state')
        self.healthState = new_stack.get('healthState')
        self.id = new_stack.get('id')
        self.instanceIds = new_stack.get('instanceIds')
        self.system = new_stack.get('system')
        self.createIndex = new_stack.get('createIndex')
        self.currentScale = new_stack.get('currentScale')
        self.fqdn = new_stack.get('fqdn')
        self.linkedServices = new_stack.get('linkedServices')
        self.publicEndpoints = new_stack.get('publicEndpoints')
        self.upgrade = new_stack.get('upgrade')
        self.service_url = '{}/{}'.format(self.object_url, self.id)
        return True

    def save(self):
        data = {
            "description": self.description,
            "lbConfig": self.lbConfig,
            "metadata": self.metadata,
            "name": self.name,
            "retainIp": self.retainIp,
            "scale": self.scale,
            "scalePolicy": self.scalePolicy,
            "selectorContainer": self.selectorContainer,
            "selectorLink": self.selectorLink
        }
        return self.env.request(self.service_url, 'PUT', data=data)

    def scale_in(self, scale):
        self.scale -= scale
        if self.scale < 0:
            self.scale += scale
            raise RequestError('Scale can\'t be lower than 0, requested {}'.format(self.scale - scale))
        return self.env.request(self.service_url, 'PUT', {"scale": self.scale})

    def scale_out(self, scale):
        self.scale += scale
        return self.env.request(self.service_url, 'PUT', {"scale": self.scale})

    def scale_to(self, scale):
        if scale < 0:
            raise RequestError('Scale can\'t be lower than 0, requested {}'.format(self.scale - scale))
        self.scale = scale
        return self.env.request(self.service_url, 'PUT', {"scale": self.scale})

    # http://docs.rancher.com/rancher/v1.3/en/api/v2-beta/api-resources/serviceLog/
    def logs(self):
        return self.env.request('{}/servicelogs'.format(self.service_url), 'GET')

    # Actions

    def activate(self):
        return self.action('activate')

    def cancel_upgrade(self):
        return self.action('cancelupgrade')

    def continue_upgrade(self):
        return self.action('continueupgrade')

    def deactivate(self):
        return self.action('deactivate')

    def finish_upgrade(self):
        return self.action('finishupgrade')

    def rollback(self):
        return self.action('rollback')

    def add_service_link(self, service_link):
        return self.action('addservicelink', data=service_link)

    def remove_service_link(self, service_link):
        return self.action('removeservicelink', data=service_link)

    def restart(self, rolling_restart_strategy):
        return self.action('restart', data=rolling_restart_strategy)

    def set_service_links(self, service_links):
        return self.action('setservicelinks', data=service_links)

    def service_upgrade(self, in_service_strategy, to_service_strategy):
        return self.action('upgrade', data={'inServiceStrategy': in_service_strategy,
                                            'toServiceStrategy': to_service_strategy})
