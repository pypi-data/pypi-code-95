from docopt import docopt

from .command_auth import AuthCommand
from .util.type_util import IntegrationType, TypeUtil


class List(AuthCommand):
    def usage(self, hidden=False):
        return """
Usage:
    rock list [-h]
    rock list collections [--workspace=WORKSPACE]
    rock list integrations
    rock list workspaces{}

Options:
  -h, --help                      show this help message and exit
  -w, --workspace=WORKSPACE       list all collections recursively within given workspace
        """.format(
            "" if not hidden else """
    rock list c [--workspace=WORKSPACE]
    rock list col [--workspace=WORKSPACE]
    rock list collection [--workspace=WORKSPACE]
    rock list i
    rock list int
    rock list integration
    rock list w
    rock list ws
    rock list workspace"""
        )

    def parse_args(self, args):
        parsed = dict(docopt(self.usage(hidden=True), argv=args, help=False))

        if parsed['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        if any(
            [
                parsed.get(t, 'None')
                for t in ['c', 'col', 'collection', 'collections']
            ]
        ):
            return {
                'resource': TypeUtil.TYPE_COLLECTION,
                'workspace': parsed['--workspace'],
            }

        if any(
            [
                parsed.get(t, 'None')
                for t in ['i', 'int', 'integration', 'integrations']
            ]
        ):
            return {'resource': TypeUtil.TYPE_INTEGRATION}

        if any(
            [
                parsed.get(t, 'None')
                for t in ['w', 'ws', 'workspace', 'workspaces']
            ]
        ):
            return {'resource': TypeUtil.TYPE_WORKSPACE}

        return {
            'resource': TypeUtil.TYPE_COLLECTION,
            'workspace': parsed['--workspace']
        }

    def go(self):
        if self.resource == TypeUtil.TYPE_COLLECTION:
            return self.go_collections()

        if self.resource == TypeUtil.TYPE_INTEGRATION:
            return self.go_integrations()

        if self.resource == TypeUtil.TYPE_WORKSPACE:
            return self.go_workspaces()

        return self.go_collections()

    def go_collections(self):
        fields = [
            'name', 'workspace', 'status', 'description', 'created_by',
            'created_at', 'size'
        ]
        collections = [
            c.asdict()
            for c in self.client.Collection.list(workspace=self.workspace)
        ]

        for c in collections:
            c['size'] = c.get('stats').get('total_size')
        collections.sort(
            key=lambda c: "{}.{}".format(c.get('workspace'), c.get('name'))
        )
        self.print_list(0, collections, fields)
        return 0

    def go_integrations(self):
        fields = ['type', 'name', 'description', 'created_by']
        integrations = [i.to_dict() for i in self.client.Integration.list()]
        for i in integrations:
            i['type'] = IntegrationType.parse_from_integration(i)
        integrations.sort(
            key=lambda i: "{}.{}".format(i.get('type'), i.get('name'))
        )
        self.print_list(0, integrations, fields)
        return 0

    def go_workspaces(self):
        fields = [
            'name', 'description', 'collection_count', 'created_by',
            'created_at'
        ]
        workspaces = [w.to_dict() for w in self.client.Workspace.list()]
        for w in workspaces:
            w['is_empty'] = str(w.get('collection_count') == 0)
        workspaces.sort(
            key=lambda w: "{}.{}".format(w.get('is_empty'), w.get('name'))
        )
        self.print_list(0, workspaces, fields)
        return 0
