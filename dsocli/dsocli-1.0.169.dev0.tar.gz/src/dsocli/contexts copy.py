
import re
import os
import sys
import imp
import yaml
from .enum_utils import OrderedEnum
from .constants import *
from .logger import Logger
from .dict_utils import *
from pathlib import Path
from .file_utils import *
from .exceptions import DSOException
from .stages import Stages
from .constants import *
from .exceptions import DSOException


class ContextScope(OrderedEnum):
    Application = 10
    Project = 20
    Global = 30


class ConfigScope(OrderedEnum):
    Local = 10
    Middle = 20
    Global = 30


context_translation_matrix = {
    'default': {
        'default': {
            'default': {
                'default': {
                    '0': "Global",
                },
                'stage': {
                    '0': "Global Stage",
                    'n': "Global Numbered Stage",
                },
            },
        },
        'project': {
            'default': {
                'default': {
                    '0': "Project",
                },
                'stage': {
                    '0': "Project Stage",
                    'n': "Project Numbered Stage",
                },
            },
            'application': {
                'default': {
                    '0': "Application",
                },
                'stage': {
                    '0': "Application Stage",
                    'n': "Application Numbered Stage",
                },
            },
        },
    },
    'namespace': {
        'default': {
            'default': {
                'default': {
                    '0': "Global",
                },
                'stage': {
                    '0': "Global Stage",
                    'n': "Global Numbered Stage",
                },
            },
        },
        'project': {
            'default': {
                'default': {
                    '0': "Project",
                },
                'stage': {
                    '0': "Project Stage",
                    'n': "Project Numbered Stage",
                },
            },
            'application': {
                'default': {
                    '0': "Application",
                },
                'stage': {
                    '0': "Application Stage",
                    'n': "Application Numbered Stage",
                },
            },
        },
    }

}


_default_config = {
    'kind': 'dso/config',
    'version': 1,
    # 'namespace': 'default',
    # 'project': 'default',
    # 'application': 'default',
    # 'stage': 'default',
    'contexts': [
        {
            'name': 'default',
            'spec': {
                'namespace': 'default',
                'project': 'default',
                'application': 'default',
                'stage': 'default',
            }
        },
    ],
}


def get_default_config():
    return _default_config.copy()



class Context():

    def __init__(self, namespace=None, project=None, application=None, stage=None, scope=ContextScope.Application):
        # self.namespace = namespace
        # self.project = project
        # self.application = application
        # self.stage = stage
        # self._scope = scope
        
        self.set_namespace(namespace)
        self.set_project(project)
        self.set_application(application)
        self.set_stage(stage)
        self._scope = scope

    def __str__(self):
        return f"namespace={self.namespace}, project={self.project}, application={self.application}, stage={self.short_stage}"


    @property
    def namespace(self):
        return self._namespace

    def set_namespace(self, value):
        if value:
            self._namespace = value
        else:
            if 'DSO_NAMESPACE' in os.environ:
                self._namespace = os.getenv('DSO_NAMESPACE').lower() or 'default'
            else:
                self._namespace = 'default'


    @property
    def project(self):
        return self.get_project()

    def get_project(self, ignore_scope=False):
        if ignore_scope:
            result = self._project
        else:
            if self._scope > ContextScope.Project:
                result = 'default'
                Logger.warn("Switched to the global scope.")
            else:
                result = self._project
        return result

    def set_project(self, value):
        if value:
            self._project = value
        else:
            if 'DSO_PROJECT' in os.environ:
                self._project = os.getenv('DSO_PROJECT').lower() or 'default'
            else:
                self._project = 'default'

    @property
    def application(self):
        return self.get_application()

    def get_application(self, ignore_scope=False):
        if ignore_scope:
            result = self._application
        else:
            if self._scope > ContextScope.Application:
                result = 'default'
                Logger.warn("Switched to the project scope.")
            else:
                result = self._application
        return result


    def set_application(self, value):
        if value:
            self._application = value
        else:
            if 'DSO_APPLICATON' in os.environ:
                self._application = os.getenv('DSO_APPLICATON').lower() or 'default'
            else:
                self._application = 'default'

    @property
    def stage(self):
        return self._stage

    def set_stage(self, value):
        if value:
            self._stage = value
        else:
            if 'DSO_STAGE' in os.environ:
                self._stage = os.getenv('DSO_STAGE').lower() or Stages.default_stage
            else:
                self._stage = Stages.default_stage
        
        self._stage = Stages.normalize( self._stage)
        self._short_stage = Stages.shorten(self._stage)


    @property
    def short_stage(self):
        return self._short_stage


    @property
    def scope(self):
        return self._scope


    @property
    def scope_translation(self):
        namespace_idx = 'default' if self.namespace == 'default' else 'namespace'
        project_idx = 'default' if self.project == 'default' else 'project'
        application_idx = 'default' if self.application == 'default' else 'application'
        stage_idx = 'default' if Stages.is_default(self.stage) else 'stage'
        n_idx = '0' if Stages.is_default_env(self.stage) else 'n'
        return context_translation_matrix[namespace_idx][project_idx][application_idx][stage_idx][n_idx]


    def get_path(self, key=None):
        result = f"/{self.namespace}/{self.project}"
        ### every application must belong to a project, no application overrides allowed in the default project
        if not self.project == 'default':
            result += f"/{self.application}"
        else:
            result += "/default"
        result += f"/{self.stage}"
        if key:
            result += f"/{key}"
        return result


class ContextService():

    @property
    def config_dir(self):
        return '.dso'

    @property
    def config_file(self):
        return 'config.yml'

    context = Context()
    working_dir = ''
    local_config = {}
    local_config_file_path = ''
    local_config_dir_path = ''
    global_config = {}
    global_config_file_path = ''
    global_config_dir_path = ''
    inherited_config = {}
    inherited_config_files = []
    merged_config = {}


    def load(self, working_dir, context_name=None, namespace=None, project=None, application=None, stage=None, scope=ContextScope.Application):
        self.working_dir = working_dir
        self.update_merged_config()
        self.load_global_config()
        self.load_inherited_config()
        self.load_local_config()
        self.load_context(context_name, namespace, project, application, stage, scope)
        self.check_version()


    @property
    def meta_vars(self):
        return {'dso': self.merged_config}


    def load_context(self, context_name, namespace, project, application, stage, scope):

        if context_name:
            found = self.get_contexts(context_name)
            if not found:
                raise DSOException(f"Context '{context_name}' not found.")
            self._namespace = found[-1]['spec']['namespace']
            self._project = found[-1]['spec']['project']
            self._application = found[-1]['spec']['application']
            self._stage = found[-1]['spec']['stage']
        else:
            self._namespace = 'default'
            self._project = 'default'
            self._application = 'default'
            self._stage = 'default'

        if namespace:
            if not namespace == self._namespace:
                self._namespace = namespace
                Logger.debug(f"Namespace overidden from '{self._namespace}' to '{namespace}'.")
        else:
            if 'DSO_NAMESPACE' in os.environ:
                ev_namespace = os.getenv('DSO_NAMESPACE').lower() or 'default'
                if not ev_namespace == self._namespace:
                    self._namespace = ev_namespace
                    Logger.debug(f"Environment variable 'DSO_NAMESPACE' used.")

        if project:
            if not project == self._project:
                self._project = project
                Logger.debug(f"Project overidden from '{self._project}' to '{project}'.")
        else:
            if 'DSO_PROJECT' in os.environ:
                ev_project = os.getenv('DSO_PROJECT').lower() or 'default'
                if not ev_project == self._project:
                    self._project = ev_project
                    Logger.debug(f"Environment variable 'DSO_PROJECT' used.")

        if application:
            if not application == self._application:
                self._application = application
                Logger.debug(f"Project overidden from '{self._application}' to '{application}'.")
        else:
            if 'DSO_APPLICATION' in os.environ:
                ev_application = os.getenv('DSO_APPLICATION').lower() or 'default'
                if not ev_application == self._application:
                    self._application = ev_application
                    Logger.debug(f"Environment variable 'DSO_APPLICATION' used.")

        if stage:
            if not stage == self._stage:
                self._stage = stage
                Logger.debug(f"Project overidden from '{self._stage}' to '{stage}'.")
        else:
            if 'DSO_STAGE' in os.environ:
                ev_stage = os.getenv('DSO_STAGE').lower() or 'default'
                if not ev_stage == self._stage:
                    self._stage = ev_stage
                    Logger.debug(f"Environment variable 'DSO_STAGE' used.")
        self._short_stage = Stages.shorten(self._stage)

        self._scope = scope
        self.context = Context(self._namespace, self._project, self._application, self._stage, self._scope)


    def load_global_config(self):
        self.global_config = {}
        self.global_config_dir_path = os.path.join(Path.home(), self.config_dir)
        self.global_config_file_path = os.path.join(self.global_config_dir_path, self.config_file)

        if not os.path.exists(self.global_config_file_path):
            Logger.debug("Global DSO configuration not found.")
            return

        Logger.debug(f"Global DSO configuration found: path={self.global_config_file_path}")
        try:
            self.global_config_raw = load_file(self.global_config_file_path)
            self.global_config = load_file(self.global_config_file_path, pre_render_values=self.meta_vars)
        except:
            raise
            raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(self.global_config_file_path))

        self.update_merged_config()


    def load_local_config(self, silent=False):
        self.local_config_raw = {}
        self.local_config = {}
        self.local_config_dir_path = os.path.join(self.working_dir, self.config_dir)
        self.local_config_file_path = os.path.join(self.local_config_dir_path, self.config_file)

        if not os.path.exists(self.local_config_file_path):
            if not silent:
                Logger.warn(MESSAGES['NoDSOConfigFound'])
            return

        Logger.debug(f"Local DSO configuration found: path={self.local_config_file_path}")

        try:
            self.local_config_raw = load_file(self.local_config_file_path)
            self.local_config = load_file(self.local_config_file_path, pre_render_values=self.meta_vars)
        except:
            raise
            raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(self.local_config_file_path))

        self.update_merged_config()

    def load_inherited_config(self):

        self.inherited_config = {}

        for dir in Path(self.working_dir).resolve().parents:
            configFilePath = os.path.join(dir, self.config_dir, self.config_file)
            if os.path.exists(configFilePath):
                if not os.path.samefile(configFilePath, self.global_config_file_path):
                    Logger.debug(f"Inherited DSO configuration found: path={configFilePath}")
                    self.inherited_config_files.append(configFilePath)


        for configFilePath in reversed(self.inherited_config_files):
            try:
                config = load_file(configFilePath, self.meta_vars)
            except:
                raise
                raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(configFilePath))
            
            self.inherited_config = merge_dicts(config, self.inherited_config)

        self.update_merged_config()



    def update_merged_config(self):
        self.merged_config = get_default_config()
        merge_dicts(self.global_config, self.merged_config)
        merge_dicts(self.inherited_config, self.merged_config)
        merge_dicts(self.local_config, self.merged_config)
        
        ### add context 
        self.merged_config['namespace'] = self.context.namespace
        self.merged_config['project'] = self.context.project
        self.merged_config['application'] = self.context.application
        self.merged_config['stage'] = self.context.stage
        self.merged_config['scope'] = str(self.context.scope)



    def check_version(self):
        if not int(self.merged_config['version']) == int(_default_config['version']):
            if int(self.merged_config['version']) > int(_default_config['version']):
                Logger.warn(MESSAGES['DSOConfigNewer'].format(_default_config['version'], self.merged_config['version']))
            else:
                Logger.warn(MESSAGES['DSOConfigOlder'].format(_default_config['version'], self.merged_config['version']))


    def save_local_config(self):
        os.makedirs(self.local_config_dir_path, exist_ok=True)
        save_data(self.local_config_raw, self.local_config_file_path)


    def save_global_config(self):
        os.makedirs(self.global_config_dir_path, exist_ok=True)
        save_data(self.global_config_raw, self.global_config_file_path)


    @property
    def contexts(self):
        return self.get_contexts()

    def get_contexts(self, name=None):
        try:
            result = self.merged_config['contexts']
        except nameError:
            raise DSOException("Invalid dso configuration schema.")
        if not name:
            return result
        else:
            found = [x for x in result if x['name'] == name]
            return found if found else []

    @property
    def namespace(self):
        return self.context.namespace

    # @property
    # def namespace(self):
    #     return self.get_namespace()
        
    # def get_namespace(self):
    #     if 'namespace' in self.local_config:
    #         result = self.local_config['namespace'].lower() or 'default'

    #     elif 'DSO_NAMESPACE' in os.environ:
    #         result = os.getenv('DSO_NAMESPACE').lower() or 'default'

    #     elif 'namespace' in self.inherited_config:
    #         result = self.inherited_config['namespace'].lower() or 'default'

    #     elif 'namespace' in self.global_config:
    #         result = self.global_config['namespace'].lower() or 'default'

    #     else:
    #         result = 'default'

    #     return result

    @property
    def project(self):
        return self.context.project


    # @property
    # def project(self):
    #     return self.get_project()

    # def get_project(self):
    #     if 'project' in self.local_config:
    #         result = self.local_config['project'].lower() or 'default'

    #     elif 'DSO_PROJECT' in os.environ:
    #         result = os.getenv('DSO_PROJECT').lower() or 'default'

    #     elif 'project' in self.inherited_config:
    #         result = self.inherited_config['project'].lower() or 'default'

    #     elif 'project' in self.global_config:
    #         result = self.global_config['project'].lower() or 'default'

    #     else:
    #         result = 'default'

    #     return result

    @property
    def application(self):
        return self.context.application


    # @property
    # def application(self):
    #     return self.get_application()

    # def get_application(self):
    #     if 'application' in self.local_config:
    #         result = self.local_config['application'].lower() or 'default'

    #     elif 'DSO_APPLICATION' in os.environ:
    #         result = os.getenv('DSO_APPLICATION').lower() or 'default'

    #     elif 'application' in self.inherited_config:
    #         result = self.inherited_config['application'].lower() or 'default'

    #     elif 'application' in self.global_config:
    #         result = self.global_config['application'].lower() or 'default'

    #     else:
    #         result = 'default'
        
    #     if not result == 'default' and self.project == 'default':
    #         Logger.debug(f"Application '{result}' was ignored because the global context is being used.")
    #         result = 'default'

    #     return result



    @property
    def stage(self):
        return self.context.stage



    @property
    def short_stage(self):
        return self.context.short_stage

    # @property
    # def stage(self):
    #     return self.get_stage()

    # def get_stage(self):
    #     if 'stage' in self.merged_config:
    #         return self.merged_config['stage']
    #     else: 
    #         return 'default'


    def get(self, key=None, scope=ConfigScope.Local):
        if key:
            Logger.info("Getting '{0}' from DSO configurations...".format(key))
        else:
            Logger.info("Getting DSO configurations...")

        if scope == ConfigScope.Local:
            usedConfig = merge_dicts(self.overriden_config, self.local_config.copy())
        elif scope == ConfigScope.Global:
            usedConfig = merge_dicts(self.overriden_config, self.global_config.copy())
        else:
            usedConfig = self.merged_config.copy()

        if key:
            result = get_dict_item(usedConfig, key.split('.'))
            if not result:
                raise DSOException(f"DSO configuration '{key}' not found.")
            return result
        else:
            return usedConfig

    def set(self, key, value, use_global):
        if use_global:
            Logger.info(f"Setting '{key}' to '{value}' in the global DSO configurations...")
            if not os.path.exists(self.local_config_file_path):
                raise DSOException("The global configuration has not been intitialized yet. Run 'dso config init --global' to initialize it.")

            set_dict_value(self.global_config_raw, key.split('.'), value, overwrite_parent=True, overwrite_children=True)
            self.save_global_config()
            self.load_global_config()
            # set_dict_value(self.global_config, key.split('.'), value, overwrite_parent=True, overwrite_children=True)
            # self.update_merged_config()
        else:
            Logger.info(f"Setting '{key}' to '{value}' in the local DSO configurations...")
            if not os.path.exists(self.local_config_file_path):
                raise DSOException("The working directory has not been intitialized yet. Run 'dso config init' to initialize it.")

            set_dict_value(self.local_config_raw, key.split('.'), value, overwrite_parent=True, overwrite_children=True)
            self.save_local_config()
            self.load_local_config()

    def delete(self, key, use_global):
        if use_global:
            Logger.info(f"Deleting '{key}' from the global DSO configurations...")
            parent = get_dict_item(self.global_config_, key.split('.')[:-1])
            if parent and key.split('.')[-1] in parent:
                parent.pop(key.split('.')[-1])
                self.save_global_config()
                self.load_global_config()
            else:
                raise DSOException(f"'{key}' not found in the global DSO configuratoins.")

        else:
            Logger.info(f"Deleting '{key}' from the local DSO configurations...")
            parent = get_dict_item(self.local_config_raw, key.split('.')[:-1])
            if parent and key.split('.')[-1] in parent:
                parent.pop(key.split('.')[-1])
                self.save_local_config()
                self.load_local_config()
            else:
                raise DSOException(f"'{key}' not found in the local DSO configuratoins.")

    def init(self, working_dir, init_config, config_overrides, use_local):
        Logger.info("Initializing DSO configurations...")
        self.working_dir = working_dir

        self.local_config_dir_path = os.path.join(self.working_dir, self.config_dir)
        self.local_config_file_path = os.path.join(self.local_config_dir_path, self.config_file)

        if os.path.exists(self.local_config_file_path):
            Logger.warn("The working directory has already been initialized.")

        config = {}
        
        ### use init_config instead of local/inherited config
        if init_config:
            config = merge_dicts(init_config, config)
            ### merge with existing local configuration?
            if use_local:
                Logger.debug("Merging local configuration...")
                self.load_local_config(True)
                config = merge_dicts(self.local_config, config)
        else:
            ### do not show warning if directory is not initialized yet
            self.load_local_config(True)
            config = merge_dicts(self.local_config, config)
            ### override locally inherited configuration?
            if use_local: 
                Logger.debug("Merging global configuration...")
                self.load_global_config()
                config = merge_dicts(self.global_config, config)

                Logger.debug("Merging inherited configuration...")
                self.load_inherited_config()
                config = merge_dicts(self.inherited_config, config)

        ### if config overrides, merge them to local
        if config_overrides:
            Logger.debug("Merging configuration overrides...")
            self.apply_config_overrides(config_overrides)
            config = merge_dicts(self.overriden_config, config)

        self.local_config = config
        self.update_merged_config()

        self.save_local_config()


    def parse_path(self, path):
        """
            path is in the form of [/]namespace/project/application/stage/env_no/[key]
        """
        parts = path.split('/')
        if not parts[0]: parts.pop(0)
        namespace = parts[0]
        project = parts[1]
        application = parts[2]
        stage = f"{parts[3]}/{parts[4]}"
        key = '/'.join(parts[5:]) if len(parts) > 5 else None
        return namespace, project, application, stage, key


    def get_hierachy_paths(self, context, key=None, path_prefix='', ignore_stage=False, uninherited=False, reverse=False):
        
        result = []
        if uninherited:
            result.append(path_prefix + context.get_path(key=key))
        else:
            ### Add the global context: /default/default/default/0
            result.append(path_prefix + Context(context.namespace, 'default', 'default', 'default/0').get_path(key))
            if not ignore_stage and not Stages.is_default(context.stage):
                ### Add global stage context
                result.append(path_prefix + Context(context.namespace, 'default', 'default', Stages.get_default_env(context.stage)).get_path(key))
                ### Add global numbered stage context
                if not Stages.is_default_env(context.stage):
                    result.append(path_prefix + Context(context.namespace, 'default', 'default', stage).get_path(key))

            if not context.project == 'default':
                ### Add the project context: /project/default/default/0
                result.append(path_prefix + Context(context.namespace, context.project, 'default', 'default/0').get_path(key))
                if not ignore_stage and not Stages.is_default(context.stage):
                    ### Add the project stage context: /project/default/stage/0
                    result.append(path_prefix + Context(context.namespace, context.project, 'default', Stages.get_default_env(context.stage)).get_path(key))
                    ### Add the project numbered stage context: /project/default/stage/env
                    if not Stages.is_default_env(context.stage):
                        result.append(path_prefix + Context(context.namespace, context.project, 'default', stage).get_path(key))
                
                if not context.application == 'default':
                    ### Add the application context: /project/application/default/0
                    result.append(path_prefix + Context(context.namespace, context.project, context.application, 'default/0').get_path(key))
                    if not ignore_stage and not Stages.is_default(context.stage):
                        ### Add the project stage context: /project/application/stage/0
                        result.append(path_prefix + Context(context.namespace, context.project, context.application, Stages.get_default_env(context.stage)).get_path(key))
                        ### Add the application numbered stage context: /dso/project/application/stage/env
                        if not Stages.is_default_env(context.stage):
                            result.append(path_prefix + Context(context.namespace, context.project, context.application, context.stage).get_path(key))

        return list(reversed(result)) if reverse else result



Contexts = ContextService()