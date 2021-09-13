from .common import CattleObject
from .exceptions import RequestError


class Stack(CattleObject):
    object_url = 'stacks'

    def __init__(self, environment, stack_id=None, stack_name=None):
        self.env = environment
        if stack_id:
            self.stack_url = '{}/{}'.format(self.object_url, stack_id)
            stack_data = environment.request(self.stack_url, 'GET')
        elif stack_name:
            self.name = stack_name
            stack_data = self.find_by_name()
            if stack_data:
                self.stack_url = '{}/{}'.format(self.object_url, stack_data.get('id'))
        else:
            # Create stack object for list fetch
            stack_data = {}
        # Read only values
        self.state = stack_data.get('state') or None
        self.healthState = stack_data.get('healthState') or None
        self.id = stack_data.get('id') or None
        self.serviceIds = stack_data.get('serviceIds') or []
        self.system = stack_data.get('system') or False
        # Write values
        self.binding = stack_data.get('binding') or {}
        self.description = stack_data.get('description') or None
        self.dockerCompose = stack_data.get('dockerCompose') or ''
        self.environment = stack_data.get('environment') or {}
        self.externalId = stack_data.get('externalId') or None
        self.group = stack_data.get('group') or None
        self.name = stack_data.get('name') or stack_name
        self.outputs = stack_data.get('outputs') or {}
        self.previousEnvironment = stack_data.get('previousEnvironment') or {}
        self.previousExternalId = stack_data.get('previousExternalId') or None
        self.rancherCompose = stack_data.get('rancherCompose') or ''
        self.startOnCreate = stack_data.get('startOnCreate') or False

    @property
    def get_metadata(self):
        if not self.id:
            raise RequestError
        json = {
            'id': self.id,
            'name': self.name,
            'url': self.env.endpoint + self.stack_url,
            'state': self.state,
            'healthState': self.healthState,
            'serviceIds': self.serviceIds,
            'system': self.system,
            'binding': self.binding,
            'description': self.description,
            'dockerCompose': self.dockerCompose,
            'env': self.environment,
            'externalId': self.externalId,
            'group': self.group,
            'outputs': self.outputs,
            'previousEnvironment': self.previousEnvironment,
            'previousExternalId': self.previousExternalId,
            'rancherCompose': self.rancherCompose,
            'startOnCreate': self.startOnCreate
        }
        return json

    def create(self):
        data = {
            'binding': self.binding,
            'description': self.description,
            'dockerCompose': self.dockerCompose,
            'env': self.environment,
            'externalId': self.externalId,
            'group': self.group,
            'name': self.name,
            'outputs': self.outputs,
            'previousEnvironment': self.previousEnvironment,
            'previousExternalId': self.previousExternalId,
            'rancherCompose': self.rancherCompose,
            'startOnCreate': self.startOnCreate
        }
        new_stack = self.env.request(self.object_url, 'POST', data=data)
        self.state = new_stack.get('state')
        self.healthState = new_stack.get('healthState')
        self.id = new_stack.get('id')
        self.serviceIds = new_stack.get('serviceIds')
        self.system = new_stack.get('system')
        self.stack_url = '{}/{}'.format(self.object_url, self.id)

    def save(self):
        if not self.id:
            raise RequestError
        data = {
            'binding': self.binding,
            'description': self.description,
            'externalId': self.externalId,
            'group': self.group,
            'name': self.name,
            'outputs': self.outputs,
            'previousEnvironment': self.previousEnvironment,
            'previousExternalId': self.previousExternalId
        }
        self.env.request(self.stack_url, 'PUT', data=data)

    # Actions

    def activate_services(self):
        return self.action('activateservices')

    def deactivate_services(self):
        return self.action('deactivateservices')

    def cancel_upgrade(self):
        return self.action('cancelupgrade')

    def finish_upgrade(self):
        return self.action('finishupgrade')

    def rollback(self):
        return self.action('rollback')

    def error(self):
        return self.action('error')

    def add_outputs(self, outputs):
        self.action('addoutputs', data=outputs)
        self.outputs.update(outputs)

    def export_config(self, service_ids):
        return self.action('exportconfig', data=service_ids)

    def upgrade(self):
        data = {
            'dockerCompose': self.dockerCompose,
            'environment': self.environment,
            'externalId': self.externalId,
            'rancherCompose': self.rancherCompose
        }
        self.action('upgrade', data=data)
