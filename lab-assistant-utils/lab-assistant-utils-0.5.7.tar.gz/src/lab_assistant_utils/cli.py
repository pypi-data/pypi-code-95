#!/usr/bin/env python

import ast

import astpretty
import os
from collections import namedtuple
from pathlib import Path
import configparser
import sys
from typing import Dict

if sys.version_info < (3, 8):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

import click


workspace = os.environ['WORKSPACE']
workspace_data = os.path.join(workspace, 'data')


@click.group()
def lab():
    pass


@lab.command()
def hello():
    click.echo('Hello!')


WorkspaceEntryPointMetadata = namedtuple('WorkspaceEntryPointMetadata',
                                         ['name', 'value', 'project_version', 'script_name', 'absolute_script_path'])


class WorkspaceCommands(click.MultiCommand):

    def list_commands(self, ctx):
        found_cli_plugins = self._cli_plugin_search()
        plugin_names = []
        if found_cli_plugins:
            plugin_names = list(found_cli_plugins.keys())
            plugin_names.sort()
        return plugin_names

    def get_command(self, ctx, folder):
        found_cli_plugins = self._cli_plugin_search()
        if folder not in found_cli_plugins:
            return None

        plugin = found_cli_plugins[folder]
        cli_plugin_script_path = plugin.absolute_script_path
        with open(cli_plugin_script_path) as f:
            tree = ast.parse(f.read(), mode='exec')
            astpretty.pprint(tree)
            project_version = ast.Assign(
                targets=[ast.Name(id='project_version', ctx=ast.Store())],
                value=ast.Constant(value=plugin.project_version))
            tree.body.insert(0, project_version)
            tree = ast.fix_missing_locations(tree)
            code = compile(tree, cli_plugin_script_path, mode='exec')
            # exec(code)
            #
            # code = compile(f.read(), cli_plugin_script_path, 'exec')
            try:
                ns = {}
                eval(code, ns, ns)
                return ns[found_cli_plugins[folder].script_name]
            except Exception as e:
                click.echo(f'Exception raised: {type(e)}, {e}')
                return None

    @staticmethod
    def _patch_ast_with_metadata(f, plugin: WorkspaceEntryPointMetadata):
        lab_assistant_utils_import = ast.Import(
            names=[ast.alias(name='lab_assistant_utils', asname=None)],
        )


        tree = ast.parse(f.read(), mode='exec')
        astpretty.pprint(tree)
        project_version = ast.Assign(
            targets=[ast.Name(id='project_version', ctx=ast.Store())],
            value=ast.Constant(value=plugin.project_version))
        tree.body.insert(0, project_version)
        tree = ast.fix_missing_locations(tree)

    @classmethod
    def _cli_plugin_search(cls) -> Dict[str, WorkspaceEntryPointMetadata]:
        cli_plugins = {}
        for folder in os.listdir(workspace):
            project_path = os.path.join(workspace, folder)
            setup_cfg_path = os.path.join(project_path, 'setup.cfg')
            if not os.path.exists(setup_cfg_path):
                continue

            setup_cfg = configparser.ConfigParser()
            setup_cfg.read(setup_cfg_path)
            if 'options.entry_points' not in setup_cfg or 'lab_assistant.cli_plugins' not in setup_cfg['options.entry_points']:
                continue

            entry_point = setup_cfg['options.entry_points']['lab_assistant.cli_plugins']
            entry_point_name, entry_point_value = map(lambda x: x.strip('\n '), entry_point.split('='))
            script_path, function_name = entry_point_value.split(':')
            script_path_parts = script_path.split('.')
            script_name = script_path_parts[-1]
            absolute_script_path = cls._find_absolute_script_path(project_path, script_name)
            if not absolute_script_path:
                click.echo(f'Error: project "{folder}" supplies a lab assistant CLI plugin but script "{script_name}" could not be loaded')
                continue

            if 'metadata' not in setup_cfg:
                click.echo(f'Error: Lab project "{folder}" detected without project metadata')
                continue

            if 'version' not in setup_cfg['metadata']:
                click.echo(f'Error: Lab project "{folder}" detected without project version metadata')
                continue

            cli_plugins[entry_point_name] = WorkspaceEntryPointMetadata(
                name=entry_point_name,
                value=entry_point_value,
                project_version=setup_cfg['metadata']['version'],
                script_name=script_name,
                absolute_script_path=absolute_script_path)
        return cli_plugins

    @staticmethod
    def _find_absolute_script_path(project_path: str, script_name: str) -> str:
        script_filename = f'{script_name}.py'
        exclude = {'.git', '.idea', '.ipynb_checkpoints', '__pycache__', '.pytest_cache', 'data'}
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in exclude]
            absolute_script_path = os.path.join(root, script_filename)
            if script_filename in files and os.path.exists(absolute_script_path):
                return absolute_script_path


class LabCliPlugins(click.MultiCommand):
    ENTRY_POINT_GROUP = 'lab_assistant.cli_plugins'

    def list_commands(self, ctx):
        eps = entry_points()[self.ENTRY_POINT_GROUP]
        plugin_names = []
        for e in eps:
            plugin_names.append(e.name)
        return plugin_names

    def get_command(self, ctx, plugin_name):
        eps = entry_points()[self.ENTRY_POINT_GROUP]
        for e in eps:
            if e.name == plugin_name:
                return e.load()


lab_cli_plugins = LabCliPlugins(help='Lab CLI plugin commands')
workspace_commands = WorkspaceCommands(help='Workspace commands')
cli = click.CommandCollection(sources=[lab, workspace_commands, lab_cli_plugins])


if __name__ == '__main__':
    cli()
