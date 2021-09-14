import sys
import os
import platform
import click
import re
import yaml
import glob
from stdiomask import getpass
from .constants import *
from .cli_constants import *
from .exceptions import DSOException
from .config import ConfigService, Configs, ConfigScope, ContextMode
from .logger import Logger, log_levels
from .stages import Stages
from .parameters import Parameters
from .secrets import Secrets
from .templates import Templates
from .networks import Networks
from .click_extend import *
from click_params import RangeParamType
from .cli_utils import *
from .file_utils import *
from functools import reduce
from .pager import Pager
from .editor import Editor
from .version import __version__
from pathlib import Path
from .dict_utils import *
from .settings import *
from .contexts import Context, ContextService, Contexts, ContextScope

DEFAULT_CLICK_CONTEXT = dict(help_option_names=['-h', '--help'])



@click.group(context_settings=DEFAULT_CLICK_CONTEXT)
def cli():
    """Mable DSO CLI"""
    pass



@cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
def config():
    """
    Manage DSO application configuration.
    """
    pass



@cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
def parameter():
    """
    Manage parameters.
    """
    pass



@cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
def secret():
    """
    Manage secrets.
    """
    pass



@cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
def template():
    """
    Manage templates.
    """
    pass



@cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
def package():
    """
    Manage build packages.
    """
    pass



@cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
def release():
    """
    Manage deployment releases.
    """
    pass

@cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
def network():
    """
    Manage IP networks.
    """
    pass

# @network.group(context_settings=DEFAULT_CLICK_CONTEXT)
# def subnet_plan():
#     """
#     Manage subnet plan.
#     """
#     pass

# @cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
# def provision():
#     """
#     Provision resources.
#     """
#     pass

# 

# @cli.group(context_settings=DEFAULT_CLICK_CONTEXT)
# def deploy():
#     """
#     Deploy releases.
#     """
#     pass





@cli.command('version', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['version']}")
def version():
    """
    Display version details.
    """
    click.echo(f"Mable DSO CLI: {__version__}\nPython: {platform.sys.version}")





@parameter.command('add', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['parameter']['add']}")
@command_doc(CLI_COMMANDS_HELP['parameter']['add'])
@click.argument('key', required=False)
@click.argument('value', required=False)
@click.option('-k', '--key', 'key_option', required=False, metavar='<key>', help=f"{CLI_PARAMETERS_HELP['parameter']['key']}")
@click.option('-v', '--value', 'value_option', metavar='<value>', required=False, help=f"{CLI_PARAMETERS_HELP['parameter']['value']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['common']['input']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv', 'shell']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
# @click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), default=str(ContextScope.Application), show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def add_parameter(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, value, value_option, input, format):
    
    parameters = []

    def validate_command_usage():
        nonlocal working_dir, key, value, parameters, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

        if input:
            validate_none_provided([key, key_option], ["KEY", "'-k' / '--key'"], ["'-i' / '--input'"])
            validate_none_provided([key, key_option], ["VALUE", "'-v' / '--value'"], ["'-i' / '--input'"])
            parameters = read_data(input, 'Parameters', ['Key', 'Value'], format)

            ### eat possible enclosing (double) quotes when source is file, stdin has already eaten them!
            if format == 'shell': 
                for param in parameters:
                    if re.match(r'^".*"$', param['Value']):
                        param['Value'] = re.sub(r'^"|"$', '', param['Value'])
                    elif re.match(r"^'.*'$", param['Value']):
                        param['Value'] = re.sub(r"^'|'$", '', param['Value'])

        ### no input file
        else:
            key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
            value = validate_only_one_provided([value, value_option], ["VALUE", "'-v' / '--value'"])
            parameters.append({'Key': key, 'Value': value})

    success = []
    failed = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        # Contexts.load(working_dir=working_dir)
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)
        # ctx = ContextService()
        # ctx.load(working_dir=working_dir, context_name=context_name, namespace=namespace, project=project, application=application, stage=stage, scope=scope)
        # cfg = ConfigService()
        # cfg.load(working_dir=working_dir, config_overrides_string=config_override, context_service=ctx)

        if len(parameters) == 0:
            Logger.warn("No parameter to add.")
        else:
            failed = [x['Key'] for x in parameters]
            for param in parameters:
                success.append(Parameters.add(Configs, param['Key'], param['Value']))
                failed.remove(param['Key'])

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if parameters:
            failure = []
            for key in failed:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@parameter.command('list', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['parameter']['list']}")
@command_doc(CLI_COMMANDS_HELP['parameter']['list'])
@click.option('-u','--uninherited', 'uninherited', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['parameter']['uninherited']}")
@click.option('--filter', required=False, metavar='<regex>', help=f"{CLI_PARAMETERS_HELP['common']['filter']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'raw', 'shell']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def list_parameter(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, uninherited, filter, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, query, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        defaultQuery = '{Parameters: Parameters[*].{Key: Key, Value: Value, Stage: Stage, Scope: Scope}}'
        query = validate_query_argument(query, query_all, defaultQuery)
        
        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(e.msg))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Parameters.list(Configs, uninherited, filter)
        if len(result['Parameters']) == 0:
            Logger.warn("No parameter found.")

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@parameter.command('get', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['parameter']['get']}")
@command_doc(CLI_COMMANDS_HELP['parameter']['get'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', required=False, metavar='<key>', help=f"{CLI_PARAMETERS_HELP['parameter']['key']}")
@click.option('--revision', metavar='<revision-id', required=False, help=f"{CLI_PARAMETERS_HELP['parameter']['revision']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def get_parameter(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, revision, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, key, query, scope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        defaultQuery = '{Value: Value}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Parameters.get(Configs, key, revision)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@parameter.command('edit', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['parameter']['edit']}")
@command_doc(CLI_COMMANDS_HELP['parameter']['edit'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['key']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def edit_parameter(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option):

    def validate_command_usage():
        nonlocal working_dir, key, scope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Parameters.list(Configs, uninherited=True, filter=f"^{key}$")
        if result['Parameters']:
            value = format_data(result, 'Parameters[0].Value', 'raw')
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(mode='w', encoding='utf-8', delete=True) as tf:
                tf.write(value)
                tf.flush()
                value, changed = Editor.edit(tf.name)
            if changed:
                Parameters.add(Configs, key, value)
            else:
                Logger.warn(CLI_MESSAGES['NoChanegeDetectedAfterEditing'])
        else:
            raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key, Configs.get_namespace(ContextMode.Requested), Configs.get_project(ContextMode.Requested), Configs.get_application(ContextMode.Requested), Configs.get_short_stage(ContextMode.Requested), Configs.scope))


    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@parameter.command('history', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['parameter']['history']}")
@command_doc(CLI_COMMANDS_HELP['parameter']['history'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', required=False, metavar='<key>', help=f"{CLI_PARAMETERS_HELP['parameter']['key']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def history_parameter(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, key, query, scope
        
        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date, Value: Value}}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Parameters.history(Configs, key)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@parameter.command('delete', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['parameter']['delete']}")
@command_doc(CLI_COMMANDS_HELP['parameter']['delete'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['parameter']['key']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['common']['input']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv', 'shell']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def delete_parameter(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, input, format):

    parameters = []

    def validate_command_usage():
        nonlocal working_dir, key, parameters, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

        if input:
            validate_none_provided([key, key_option], ["KEY", "'-k' / '--key'"], ["'-i' / '--input'"])
            parameters = read_data(input, 'Parameters', ['Key'], format)

        ### no input file
        else:
            key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
            parameters.append({'Key': key})

    success = []
    failed = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        if len(parameters) == 0:
            Logger.warn("No parameter to delete.")
        else:
            failed = [x['Key'] for x in parameters]
            for parameter in parameters:
                success.append(Parameters.delete(Configs, parameter['Key']))
                failed.remove(parameter['Key'])

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if parameters:
            failure = []
            for key in failed:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@secret.command('add', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['secret']['add']}")
@command_doc(CLI_COMMANDS_HELP['secret']['add'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', required=False, metavar='<key>', help=f"{CLI_PARAMETERS_HELP['secret']['key']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['common']['input']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv', 'shell']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def add_secret(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, input, format):

    secrets = []

    def validate_command_usage():
        nonlocal working_dir, key, secrets, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

        if input:
            validate_none_provided([key, key_option], ["KEY", "'-k' / '--key'"], ["'-i' / '--input'"])
            secrets = read_data(input, 'Secrets', ['Key', 'Value'], format)

            ### eat possible enclosing (double) quotes when source is file, stdin has already eaten them!
            if format == 'shell': 
                for secret in secrets:
                    if re.match(r'^".*"$', secret['Value']):
                        secret['Value'] = re.sub(r'^"|"$', '', secret['Value'])
                    elif re.match(r"^'.*'$", secret['Value']):
                        secret['Value'] = re.sub(r"^'|'$", '', secret['Value'])

        ### no input file
        else:
            key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
            value = getpass(" Enter secret value: ")
            value2 = getpass("Verify secret value: ")
            if not value == value2:
                raise DSOException(CLI_MESSAGES['EnteredSecretValuesNotMatched'].format(format))

            secrets.append({'Key': key, 'Value': value})

    success = []
    failed = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        if len(secrets) == 0:
            Logger.warn("No secret to add.")
        else:
            failed = [x['Key'] for x in secrets]
            for secret in secrets:
                success.append(Secrets.add(Configs, secret['Key'], secret['Value']))
                failed.remove(secret['Key'])

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if secrets:
            failure = []
            for key in failed:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@secret.command('list', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['secret']['list']}")
@command_doc(CLI_COMMANDS_HELP['secret']['list'])
@click.option('-d', '--decrypt', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['secret']['decrypt']}")
@click.option('-u','--uninherited', 'uninherited', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['secret']['uninherited']}")
@click.option('--filter', required=False, metavar='<regex>', help=f"{CLI_PARAMETERS_HELP['common']['filter']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv', 'shell']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def list_secret(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, uninherited, decrypt, filter, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, query, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        defaultQuery = '{Secrets: Secrets[*].{Key: Key, Value: Value, Scope: Scope, Origin: Origin}}'
        query = validate_query_argument(query, query_all, defaultQuery)

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(e.msg))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Secrets.list(Configs, uninherited, decrypt, filter)
        if len(result['Secrets']) == 0:
            Logger.warn("No secret found.")

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@secret.command('get', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['secret']['get']}")
@command_doc(CLI_COMMANDS_HELP['secret']['get'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', required=False, metavar='<key>', help=f"{CLI_PARAMETERS_HELP['parameter']['key']}")
@click.option('--revision', metavar='<revision-id', required=False, help=f"{CLI_PARAMETERS_HELP['parameter']['revision']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def get_secret(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, revision, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, key, query, scope
        
        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        defaultQuery = '{Value: Value}'
        query = validate_query_argument(query, query_all, defaultQuery)


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Secrets.get(Configs, key, decrypt=True, revision=revision)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@secret.command('edit', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['secret']['edit']}")
@command_doc(CLI_COMMANDS_HELP['secret']['edit'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['key']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def edit_secret(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option):

    def validate_command_usage():
        nonlocal working_dir, key, scope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Secrets.list(Configs, uninherited=True, decrypt=True, filter=f"^{key}$")
        if result['Secrets']:
            value = format_data(result, 'Secrets[0].Value', 'raw')
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(mode='w', encoding='utf-8', delete=True) as tf:
                tf.write(value)
                tf.flush()
                value, changed = Editor.edit(tf.name)
            if changed:
                Secrets.add(Configs, key, value)
            else:
                Logger.warn(CLI_MESSAGES['NoChanegeDetectedAfterEditing'])
        else:
            raise DSOException(CLI_MESSAGES['SecretNotFound'].format(key, Configs.get_namespace(ContextMode.Requested), Configs.get_project(ContextMode.Requested), Configs.get_application(ContextMode.Requested), Configs.get_short_stage(ContextMode.Requested), Configs.scope))


    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@secret.command('history', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['secret']['history']}")
@command_doc(CLI_COMMANDS_HELP['secret']['history'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', required=False, metavar='<key>', help=f"{CLI_PARAMETERS_HELP['parameter']['key']}")
@click.option('-d', '--decrypt', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['secret']['decrypt']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def history_secret(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, decrypt, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, key, query, scope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date, Value: Value}}'
        query = validate_query_argument(query, query_all, defaultQuery)


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Secrets.history(Configs, key, decrypt)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@secret.command('delete', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['secret']['delete']}")
@command_doc(CLI_COMMANDS_HELP['secret']['delete'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['secret']['key']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['common']['input']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv', 'shell']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def delete_secret(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, input, format):

    secrets = []

    def validate_command_usage():
        nonlocal working_dir, key, secrets, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

        if input:
            validate_none_provided([key, key_option], ["KEY", "'-k' / '--key'"], ["'-i' / '--input'"])
            secrets = read_data(input, 'Secrets', ['Key'], format)

        ### no input file
        else:
            key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
            secrets.append({'Key': key})

    success = []
    failed = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        if len(secrets) == 0:
            Logger.warn("No secret to delete.")
        else:
            failed = [x['Key'] for x in secrets]
            for secret in secrets:
                success.append(Secrets.delete(Configs, secret['Key']))
                failed.remove(secret['Key'])

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if secrets:
            failure = []
            for key in failed:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)



@template.command('add', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['template']['add']}")
@command_doc(CLI_COMMANDS_HELP['template']['add'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['key']}")
@click.option('-c', '--contents', 'contents_path',metavar='<path>', required=False, type=click.Path(exists=False, file_okay=True, dir_okay=True), callback=check_file_path, help=f"{CLI_PARAMETERS_HELP['template']['contents_path']}")
@click.option('--recursive', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['template']['recursive']}")
@click.option('-r', '--render-path', show_default=True, metavar='<path>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['render_path']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['common']['input']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def add_template(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, render_path, contents_path, recursive, input, format):

    templates = []

    def process_key_from_path(path):

        if not key:
            if os.path.samefile(path, contents_path):
                return os.path.basename(path)
            else:
                return path[len(contents_path)+1:]

        result = key
        ### if ** exist in key, replace it with path dirname
        if os.path.dirname(path)[len(contents_path):]:
            result = result.replace('**', os.path.dirname(path)[len(contents_path)+1:])
        else:
            result = result.replace('**', '')
        ### if * exist in key, replace it with path basename
        result = result.replace('*', os.path.basename(path))
        ### fix possiblly created // to /
        result = result.replace(f'{os.sep}{os.sep}', os.sep)
        ### fix possiblly trailing /
        result = re.sub(f'{os.sep}$', '', result)

        return result


    def process_render_path_from_key(key):

        if not render_path or render_path in ['.', f'.{os.sep}']:
            return key

        result = render_path
        ### if ** exist in render_path, replace it with key dirname
        if os.path.dirname(key):
            result = result.replace('**', os.path.dirname(key))
        else:
            result = result.replace('**', '')
        ### if * exist in key, replace it with path basename
        result = result.replace('*', os.path.basename(key))
        ### fix possiblly created // to /
        result = result.replace(f'{os.sep}{os.sep}', os.sep)
        ### fix possiblly trailing /
        result = re.sub(f'{os.sep}$', '', result)

        if os.path.isabs(result):
            Logger.warn(CLI_MESSAGES['RenderPathNotReleative'].format(result))
        else:
            if not result.startswith(f".{os.sep}"):
                result = os.path.join(f".{os.sep}", result)

        if os.path.isdir(result):
            raise DSOException(CLI_MESSAGES['InvalidRenderPathExistingDir'].format(result))

        return result

    def validate_command_usage():
        nonlocal working_dir, contents_path, key, templates, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

        if input:
            validate_none_provided([key, key_option], ["KEY", "'-k' / '--key'"], ["'-i' / '--input'"])
            validate_none_provided([contents_path], ["'-c', '--contents'"], ["'-i' / '--input'"])
            validate_none_provided([render_path], ["'-r' / '--render-path'"], ["'-i' / '--input'"])
            templates = read_data(input, 'Templates', ['Key', 'Contents', 'RenderPath'], format)

        ### no input file
        else:
            key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
            validate_provided(contents_path, "'-c', '--contents'")

            if os.path.isdir(contents_path):
                ### remove possible trailing /
                contents_path = re.sub(f'{os.sep}$', '', contents_path)
                if recursive:
                    globe =  f'{os.sep}**'
                else:
                    globe = f'{os.sep}*'
                path = contents_path + globe

            else:
                path = contents_path

            ### processing templates from path
            for item in glob.glob(path, recursive=recursive):
                if not Path(item).is_file(): continue
                if is_binary_file(item):
                    Logger.warn(f"Binary file '{item}' ignored.")
                    continue
                p = str(item)
                k = process_key_from_path(p)
                r = process_render_path_from_key(k)
                templates.append({'Key': k, 'Contents': open(p, encoding='utf-8', mode='r').read(), 'RenderPath': r})

    success = []
    failed = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        if len(templates) == 0:
            Logger.warn("No template to add.")
        else:
            failed = [x['Key'] for x in templates]
            for template in templates:
                success.append(Templates.add(Configs, template['Key'], template['Contents'], template['RenderPath']))
                failed.remove(template['Key'])

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if templates:
            failure = []
            for key in failed:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@template.command('list', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['template']['list']}")
@command_doc(CLI_COMMANDS_HELP['template']['list'])
@click.option('-u','--uninherited', 'uninherited', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['template']['uninherited']}")
@click.option('-c', '--contents', 'include_contents', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['template']['include_contents']}")
@click.option('--filter', required=False, metavar='<regex>', help=f"{CLI_PARAMETERS_HELP['common']['filter']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'raw']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def list_template(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, uninherited, include_contents, filter, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, query, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        if include_contents:
            defaultQuery = '{Templates: Templates[*].{Key: Key, Stage: Stage, Scope: Scope, RenderPath: RenderPath, Contents: Contents}}'
        else:
            defaultQuery = '{Templates: Templates[*].{Key: Key, Stage: Stage, Scope: Scope, RenderPath: RenderPath}}'
        query = validate_query_argument(query, query_all, defaultQuery)


        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(e.msg))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Templates.list(Configs, uninherited, include_contents, filter)
        if len(result['Templates']) == 0:
            Logger.warn("No template found.")

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)




@template.command('get', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['template']['get']}")
@command_doc(CLI_COMMANDS_HELP['template']['get'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['key']}")
@click.option('--revision', metavar='<revision-id', required=False, help=f"{CLI_PARAMETERS_HELP['parameter']['revision']}")
@click.option('-c', '--contents', 'include_contents', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['template']['include_contents']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def get_template(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, revision, include_contents, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, key, query, scope
        
        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        defaultQuery = '{Contents: Contents}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Templates.get(Configs, key, revision)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@template.command('edit', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['template']['edit']}")
@command_doc(CLI_COMMANDS_HELP['template']['get'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['key']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def edit_template(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option):

    def validate_command_usage():
        nonlocal working_dir, key, scope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Templates.list(Configs, uninherited=True, include_contents=True, filter=f"^{key}$")
        if result['Templates']:
            contents = format_data(result, '{Contents: Templates[0].Contents}', 'raw')
            renderPath = format_data(result, '{RenderPath: Templates[0].RenderPath}', 'raw')
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(mode='w', encoding='utf-8', delete=True) as tf:
                tf.write(contents)
                tf.flush()
                contents, changed = Editor.edit(tf.name)
            if changed:
                Templates.add(Configs, key, contents, renderPath)
            else:
                Logger.warn(CLI_MESSAGES['NoChanegeDetectedAfterEditing'])
        else:
            raise DSOException(CLI_MESSAGES['TemplateNotFound'].format(key, Configs.get_namespace(ContextMode.Requested), Configs.get_project(ContextMode.Requested), Configs.get_application(ContextMode.Requested), Configs.get_short_stage(ContextMode.Requested), Configs.scope))

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@template.command('history', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['template']['history']}")
@command_doc(CLI_COMMANDS_HELP['template']['history'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['key']}")
@click.option('-c', '--contents', 'include_contents', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['template']['include_contents']}")
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['query_all']}")
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['query']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def history_template(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, include_contents, query_all, query, format):

    def validate_command_usage():
        nonlocal working_dir, key, query, scope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        if include_contents:
            defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date, Contents: Contents}}'
        else:
            defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date}}'
        query = validate_query_argument(query, query_all, defaultQuery)


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Templates.history(Configs, key, include_contents)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@template.command('delete', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['template']['delete']}")
@command_doc(CLI_COMMANDS_HELP['template']['delete'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<key>', required=False, help=f"{CLI_PARAMETERS_HELP['template']['key']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['common']['input']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def delete_template(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, input, format):

    templates = []

    def validate_command_usage():
        nonlocal working_dir, key, templates, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

        if input:
            validate_none_provided([key, key_option], ["KEY", "'-k' / '--key'"], ["'-i' / '--input'"])
            templates = read_data(input, 'Templates', ['Key'], format)
        ### no input file
        else:
            key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
            templates.append({'Key': key})

    success = []
    failed = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        if len(templates) == 0:
            Logger.warn("No template to delete.")
        else:
            failed = [x['Key'] for x in templates]
            for template in templates:
                success.append(Templates.delete(Configs, template['Key']))
                failed.remove(template['Key'])

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if templates:
            failure = []
            for key in failed:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@template.command('render', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['template']['render']}")
@command_doc(CLI_COMMANDS_HELP['template']['render'])
@click.option('--filter', required=False, metavar='<regex>', help=f"{CLI_PARAMETERS_HELP['common']['filter']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def render_template(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, filter):

    def validate_command_usage():
        nonlocal working_dir, scope
        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(e.msg))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)
        response = Templates.render(Configs, filter)
        if response:
            result = {'Success': response, 'Failure': []}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)





@package.command('list', context_settings=DEFAULT_CLICK_CONTEXT, short_help="List available packages")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def list_package(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, format):
    """
    Return the list of all available packages generated for a stage.\n
    \tENV: Name of the environment
    """
    
    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@package.command('download', context_settings=DEFAULT_CLICK_CONTEXT, short_help="Download a package")
@click.option('-p', '--package', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def download_package(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, package, format):
    """
    Downlaod a package generated for a stage.\n
    \tENV: Name of the environment\n
    \tPACKAGE: Version of the package to download
    """

    def validate_command_usage():
        pass

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@package.command('create', context_settings=DEFAULT_CLICK_CONTEXT, short_help="Create a package")
@click.option('-d', '--description', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def create_package(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, description, format):
    """
    Create a new build package for the application.\n
    \tENV: Name of the environment\n
    \tDESCRIPTION (optional): Description of the package
    """

    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@package.command('delete', context_settings=DEFAULT_CLICK_CONTEXT, short_help="Delete a package")
@click.option('-p', '--package', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def delete_package(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, package, format):
    """
    Delete a package from a stage.\n
    \tENV: Name of the environment\n
    \tPACKAGE: Version of the package to be deleted
    """

    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@release.command('list', context_settings=DEFAULT_CLICK_CONTEXT, short_help="List available releases")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def list_release(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, format):
    """
    Return the list of all available releases generated for a stage.\n
    \tENV: Name of the environment
    """

    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@release.command('download', context_settings=DEFAULT_CLICK_CONTEXT, short_help="Download a release")
@click.option('-r', '--release', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def download_release(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, release, format):
    """
    Downlaod a release generated for a stage.\n
    \tENV: Name of the environment\n
    \tRELEASE: Version of the release
    """

    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@release.command('create', context_settings=DEFAULT_CLICK_CONTEXT, short_help="Create a release")
@click.option('-d', '--description', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def create_release(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, description, format):
    """
    Create a new release for a stage.\n
    \tENV: Name of the environment\n
    \tPACKAGE: Version of the package to be used for creating the release\n
    \tDESCRIPTION (optional): Description of the release
    """

    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@release.command('delete', context_settings=DEFAULT_CLICK_CONTEXT, short_help="Delete a release")
@click.option('-r', '--release', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def delete_release(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, release, format):
    """
    Delete a release from a stage.\n
    \tENV: Name of the environment\n
    \tRELEASE: Version of the release to be deleted
    """

    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@release.command('deploy', context_settings=DEFAULT_CLICK_CONTEXT, short_help="Deploy a release")
@click.option('-r', '--release', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'raw', 'csv']), default='json', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def deploy_release(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, release, format):
    """
    Delete a release from a stage.\n
    \tENV: Name of the environment\n
    \tRELEASE: Version of the release to be deleted
    """

    def validate_command_usage():
        pass


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        raise NotImplementedError("Not implemented.")
    
    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@config.command('get', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['config']['get']}")
@command_doc(CLI_COMMANDS_HELP['config']['get'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<value>', required=False, help=f"{CLI_PARAMETERS_HELP['config']['key']}")
@click.option('-l','--local', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['config']['local']}")
@click.option('-g','--global', 'global_', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['config']['global']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def get_config(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, local, global_):

    configScope = None

    def validate_command_usage():
        nonlocal working_dir, key, scope, configScope

        if not working_dir: working_dir = os.getcwd()

        key = validate_not_all_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        validate_not_all_provided([local, global_], ["'-l' / '--local'", "'-g' / '--global'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        configScope = ConfigScope.Local if local else ConfigScope.Global if global_ else ConfigScope.Merged

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        result = Configs.get(key, configScope)
        if result:
            ### pyyaml adding three trailing dots issue workaround
            if not isinstance(result, dict):
                output = yaml.dump(result, default_style='"', sort_keys=False, indent=2).rstrip()
                ### remove enclosing "
                output = output[1:len(output)-1]
            else:
                output = yaml.dump(result, sort_keys=False, indent=2).rstrip()

            Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@config.command('set', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['config']['set']}")
@command_doc(CLI_COMMANDS_HELP['config']['set'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<value>', required=False, help=f"{CLI_PARAMETERS_HELP['config']['key']}")
@click.argument('value', required=False)
@click.option('-v', '--value', 'value_option', metavar='<value>', required=False, help=f"{CLI_PARAMETERS_HELP['config']['value']}")
@click.option('-g','--global', 'global_', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['config']['global']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['config']['input']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def set_config(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, value, value_option, global_, input):

    configScope = None

    def validate_command_usage():
        nonlocal working_dir, key, value, scope, configScope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        configScope = ConfigScope.Global if global_ else ConfigScope.Local

        if input:
            validate_none_provided([value, value_option], ["VALUE", "'-v' / '--value'"], ["'-i' / '--input'"])
            try:
                value = yaml.load(input, yaml.SafeLoader)
            # except yaml.YAMLError as e:
            except:
                raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format('yaml'))
        else:
            value = validate_only_one_provided([value, value_option], ["VALUE", "'-v' / '--value'"])

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()

        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        Configs.set(key, value, configScope)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@config.command('unset', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['config']['unset']}")
@command_doc(CLI_COMMANDS_HELP['config']['unset'])
@click.argument('key', required=False)
@click.option('-k', '--key', 'key_option', metavar='<value>', required=False, help=f"{CLI_PARAMETERS_HELP['config']['key']}")
@click.option('-g','--global', 'global_', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['config']['global']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def unset_config(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, key, key_option, global_):

    configScope = None

    def validate_command_usage():
        nonlocal working_dir, key, scope, configScope

        if not working_dir: working_dir = os.getcwd()

        key = validate_only_one_provided([key, key_option], ["KEY", "'-k' / '--key'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        configScope = ConfigScope.Global if global_ else ConfigScope.Local

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()

        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        Configs.unset(key, configScope)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@config.command('init', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['config']['init']}")
@command_doc(CLI_COMMANDS_HELP['config']['init'])
@click.option('--setup', is_flag=True, required=False, help=f"{CLI_PARAMETERS_HELP['config']['setup']}")
@click.option('--override-inherited', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['config']['override_inherited']}")
@click.option('-g', '--global', 'global_', is_flag=True, default=False, help=f"{CLI_PARAMETERS_HELP['config']['global']}")
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=f"{CLI_PARAMETERS_HELP['config']['input']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def init_config(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, setup, override_inherited, global_, input):

    init_config = None
    configScope = None

    def validate_command_usage():
        nonlocal working_dir, scope, init_config, configScope

        if not working_dir: working_dir = os.getcwd()
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application
        configScope = ConfigScope.Global if global_ else ConfigScope.Local

        if input:
            # if local:
            #     Logger.warn("Option '--local' is not needed when '--input' specifies the initial configuration, as it will always be overriden locally.")
            try:
                init_config = yaml.load(input, yaml.SafeLoader)
            except:
                raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format('yaml'))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        # Configs.load(working_dir if working_dir else os.getcwd(),
        #                 'global' if global_scope else 'project' if project_scope else 'application',
        #                 config_override)
        Configs.init(working_dir, custom_init_config=init_config, config_overrides=config_override, override_inherited=override_inherited, config_scope=configScope)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)




@network.command('layout-subnet-plan', context_settings=DEFAULT_CLICK_CONTEXT, short_help=f"{CLI_COMMANDS_SHORT_HELP['network']['layout_subnet_plan']}")
@command_doc(CLI_COMMANDS_HELP['network']['layout_subnet_plan'])
@click.option('-m', '--mode', required=False, type=click.Choice(['app', 'full', 'summary']), default='app', show_default=True, help=f"{CLI_PARAMETERS_HELP['network']['subnet_layout_mode']}")
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml']), default='yaml', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['format']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
# @click.option('-c', '--context', 'context_name', metavar='<context>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['context']}")
@click.option('--namespace', metavar='<namespace>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['namespace']}")
@click.option('--project', metavar='<project]', required=False, help=f"{CLI_PARAMETERS_HELP['common']['project']}")
@click.option('--application', metavar='<application>', required=False, help=f"{CLI_PARAMETERS_HELP['common']['application']}")
@click.option('-s', '--stage', metavar='<name>[/<number>]', default='default', help=f"{CLI_PARAMETERS_HELP['common']['stage']}")
@click.option('--scope', required=False, type=click.Choice(['Application', 'Project', 'Global']), help=f"{CLI_PARAMETERS_HELP['common']['scope']}")
@click.option('--global-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['global_scope']}")
@click.option('--project-scope', required=False, is_flag=True, help=f"{CLI_PARAMETERS_HELP['common']['project_scope']}")
@click.option('--config-override', 'config_override', metavar='<key>=<value>,...', required=False, help=f"{CLI_PARAMETERS_HELP['common']['config']}")
@click.option('-b', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=6), default='2', show_default=True, help=f"{CLI_PARAMETERS_HELP['common']['verbosity']}")
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=f"{CLI_PARAMETERS_HELP['common']['working_dir']}")
def network_layout_subnet_plan(namespace, project, application, stage, scope, global_scope, project_scope, verbosity, config_override, working_dir, mode, format):

    def validate_command_usage():
        nonlocal working_dir, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, project_scope], ["'--global-scope'", "'--project-scope'"])
        validate_not_all_provided([scope, project_scope], ["'--scope'", "'--project-scope'"])
        validate_not_all_provided([scope, global_scope], ["'--scope'", "'--global-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Project if project_scope else ContextScope.Application


    # def query_selector(selector):
    #     filters = list(selector[1].items())
    #     if len(filters) == 0:
    #         raise DSOException(f"Invalid network selector: {selector}")
    #     key1 = selector[0]
    #     key2, value = filters[0]
    #     query = f"{key1}.Ranges[] | [].Subnets[?{key2} == `{value}`"
    #     for key2, value in filters[1:]:
    #         query += f" && {key2} == `{value}`"
    #     query += ']'
    #     return query


    # def build_query():
    #     selectors = list(Configs.network('selector').items())
    #     if len(selectors) == 0:
    #         query = ''
    #     else:
    #         query = "SubnetPlanLayout.Layout."
    #         selector = selectors[0]
    #         query += query_selector(selector)
    #         for selector in selectors[1:]:
    #             query += " | []."
    #             query += query_selector(selector)
    #         query +=' | [0]'
    #     return query

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Configs.load(working_dir, config_override, namespace, project, application, stage, scope)

        with open(Configs.network('subnetPlan'), 'r') as f:
            subnet_plan = yaml.safe_load(f)

        if mode == 'app':
            result = Networks.layout_subnet_plan(subnet_plan, filters={'plan': Configs.network('plan'), 'selector': Configs.network('selector')}, summary=False)
            # query = build_query()
            # query = "SubnetPlanLayout.Layout.Environment.Ranges[] | [].Subnets[?Name == `default`] | [].VPC.Ranges[] | [].Subnets[?Number == `1`] | [].Workload.Ranges[] | [].Subnets[?Number == `1`] | [0]"
            # query = "SubnetPlanLayout.Layout.Environment.Ranges[]"
            # try:
            #     output = format_data(result, query, format)
            # except IndexError as e:
            #     output = ''
            # except:
            #     raise
        else:
            result = Networks.layout_subnet_plan(subnet_plan, summary=(mode == 'summary'))

        output = format_data(result, '', format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.critical(msg)
        if verbosity >= log_levels['exception']:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



modify_click_usage_error()

if __name__ == '__main__':
    cli()

