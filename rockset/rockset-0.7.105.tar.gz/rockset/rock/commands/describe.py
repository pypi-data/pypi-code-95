from .command_auth import AuthCommand
from .util.type_util import TypeUtil
from .util.parse_util import parse_collection_path
from rockset.swagger_client.api import CollectionsApi

from docopt import docopt


class Describe(AuthCommand):
    def usage(self):
        return """
usage: rock describe [-ah] <resource-type> <name> ...

Show details about collections or integrations.

arguments:
    <name>                name of the collection or integration
    <resource-type>       oneof collections or integrations.

Valid resource types:
  * collections (aka 'col')
  * integrations (aka 'int')
  * workspaces (aka 'ws')

options:
    -a, --all           display extended stats
    -h, --help          show this help message and exit"""

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args))
        if parsed_args['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        resource_type = TypeUtil.parse_resource_type(
            parsed_args['<resource-type>']
        )
        if resource_type is None:
            ret = 'Error: invalid resource type "{}"\n'.format(resource_type)
            ret += self.usage()
            raise SystemExit(ret.strip())
        return {
            "resource": {
                'type': resource_type,
                'name': parsed_args['<name>']
            }
        }

    def go(self):
        self.logger.info('describe {}'.format(self.resource))
        if self.resource["type"] == TypeUtil.TYPE_COLLECTION:
            return self.go_collection()
        elif self.resource["type"] == TypeUtil.TYPE_INTEGRATION:
            return self.go_integration()
        elif self.resource["type"] == TypeUtil.TYPE_WORKSPACE:
            return self.go_workspace()
        else:
            return 1

    def go_collection(self):
        for name in self.resource['name']:
            workspace_name, collection_name = parse_collection_path(name)
            collection = CollectionsApi(
                self.client
            ).get(workspace=workspace_name,
                  collection=collection_name).to_dict()
            collection = self.prune_empty_fields(collection)
            self.print_list(0, [collection], default='yaml')
        return 0

    def go_integration(self):
        for name in self.resource['name']:
            integration = self.client.Integration.retrieve(name).to_dict()
            integration = self.prune_empty_fields(integration)
            self.print_list(0, [integration], default='yaml')
        return 0

    def go_workspace(self):
        for name in self.resource['name']:
            workspace = self.client.Workspace.retrieve(name).to_dict()
            workspace = self.prune_empty_fields(workspace)
            self.print_list(0, [workspace], default='yaml')
        return 0
