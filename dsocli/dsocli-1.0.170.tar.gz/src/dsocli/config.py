
import os
import sys
import imp
import yaml
import jinja2
from jinja2 import meta
from .constants import *
from .logger import Logger
from .dict_utils import *
from pathlib import Path
from .file_utils import *
from .exceptions import DSOException
from .stages import Stages
from .contexts import Context, Contexts, ContextScope
from .enum_utils import OrderedEnum




class ContextSource(OrderedEnum):
    Target = 10
    Effective = 30


class ConfigScope(OrderedEnum):
    Local = 10
    Global = 20
    Merged = 30

_init_config = {
    'kind': 'dso/application/v1',
    'version': 1,
    'project': 'default',
    'application': 'default',
}

_default_config = {
    'kind': 'dso/application/v1',
    'version': 1,
    'namespace': 'default',
    'project': 'default',
    'application': 'application',
    'network':{
        'subnetPlanGroup': '',
        'subnetPlan': '',
        'selector': {}
    }, 
    'parameter': {
        'provider': {
            'id': '',
            'spec': {}
        },
    },
    'secret': {
        'provider': {
            'id': '',
            'spec': {}
        },
    },
    'template': {
        'provider': {
            'id': '',
            'spec': {}
        },
        'render': {}
    }
}


def get_init_config():
    return _init_config.copy()


def get_default_config():
    return _default_config.copy()


class ConfigService:
    @property
    def config_dir(self):
        return '.dso'

    @property
    def config_file(self):
        return 'dso.yml'

    @property
    def install_path(self):
        return os.path.dirname(os.path.abspath(__file__))

    context = Context() 
    original_context = Context()
    working_dir = ''
    local_config = {}
    local_config_rendered = {}
    local_config_file_path = ''
    local_config_dir_path = ''
    global_config = {}
    global_config_rendered = {}
    global_config_file_path = ''
    global_config_dir_path = ''
    inherited_config_rendered = {}
    inherited_config_files = []
    overriden_config = {}
    merged_config = {}



    def load(self, working_dir, config_overrides_string='', stage=None, scope=None):
        self.working_dir = working_dir
        ### call first to set meta data for rendering
        self.update_merged_config()
        self.load_global_config()
        self.load_inherited_config()
        self.load_local_config()
        self.apply_config_overrides(self.config_string_to_dict(config_overrides_string))
        self.context = Context(self.merged_config['namespace'], self.merged_config['project'], self.merged_config['application'], stage, scope)
        ### call to add context to config
        self.update_merged_config()
        self.check_version()


    @property
    def meta_vars(self):
        return {'dso': self.merged_config}


    def load_global_config(self, render=True):
        self.global_config = {}
        self.global_config_rendered = {}
        self.global_config_dir_path = os.path.join(Path.home(), self.config_dir)
        self.global_config_file_path = os.path.join(self.global_config_dir_path, self.config_file)

        if not os.path.exists(self.global_config_file_path):
            Logger.debug("Global DSO configuration not found.")
            return

        Logger.debug(f"Global DSO configuration found: path={self.global_config_file_path}")
        try:
            self.global_config = load_file(self.global_config_file_path)
            if render:
                self.global_config_rendered = load_file(self.global_config_file_path, pre_render_values=self.meta_vars)
            else:
                self.global_config_rendered = load_file(self.global_config_file_path)

        except:
            raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(self.global_config_file_path))

        self.update_merged_config()

    def load_local_config(self, silent_warnings=False, render=True):
        self.local_config = {}
        self.local_config_rendered = {}
        self.local_config_dir_path = os.path.join(self.working_dir, self.config_dir)
        self.local_config_file_path = os.path.join(self.local_config_dir_path, self.config_file)

        if not os.path.exists(self.local_config_file_path):
            if not silent_warnings: Logger.warn(MESSAGES['NoDSOConfigFound'])
            return

        Logger.debug(f"Local DSO configuration found: path={self.local_config_file_path}")

        try:
            self.local_config = load_file(self.local_config_file_path)
            if render: 
                self.local_config_rendered = load_file(self.local_config_file_path, pre_render_values=self.meta_vars)
            else:
                self.local_config_rendered = load_file(self.local_config_file_path)

        except:
            raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(self.local_config_file_path))

        self.update_merged_config()

    def load_inherited_config(self, render=True):

        self.inherited_config_rendered = {}

        for dir in Path(self.working_dir).resolve().parents:
            configFilePath = os.path.join(dir, self.config_dir, self.config_file)
            if os.path.exists(configFilePath):
                if not os.path.samefile(configFilePath, self.global_config_file_path):
                    Logger.debug(f"Inherited DSO configuration found: path={configFilePath}")
                    self.inherited_config_files.append(configFilePath)

        for configFilePath in reversed(self.inherited_config_files):
            try:
                if render:
                    config = load_file(configFilePath, pre_render_values=self.meta_vars)
                else:
                    config = load_file(configFilePath)
            except:
                raise DSOException(MESSAGES['InvalidDSOConfigurationFile'].format(configFilePath))
            
            self.inherited_config_rendered = merge_dicts(config, self.inherited_config_rendered)

        self.update_merged_config()

    def dict_to_config_string(self, dic):
        flat = flatten_dict(dic)
        return reduce(lambda x, y: f"{x[0]}={x[1]},{y[0]}={y[1]}", flat)


    def config_string_to_dict(self, config_string):
        if not config_string: return {}

        result = {}
        try:
            configs = config_string.split(',')
            for config in configs:
                if not config: continue
                key = config.split('=')[0].strip()
                value = config.split('=')[1].strip()
                set_dict_value(result, key.split('.'), value)
        except:
            raise DSOException(MESSAGES['InvalidDSOConfigOverrides'].format(config_string))

        return result


    def apply_config_overrides(self, config_overrides):
        self.overriden_config = {}
        if config_overrides:
            configs = flatten_dict(config_overrides)
            for key, value in configs.items():
                existing = get_dict_item(self.merged_config, key.split('.'))
                if not existing:
                    Logger.warn(f"DSO configuration '{key}' was not found in the merged configuration.")
                else:
                    Logger.debug(f"DSO configuration '{key}' was overriden from '{existing}' to '{value or 'default'}'.")
                set_dict_value(self.overriden_config, key.split('.'), value)

        self.update_merged_config()


    def update_merged_config(self):
        self.merged_config = get_default_config()
        merge_dicts(self.global_config_rendered, self.merged_config)
        merge_dicts(self.inherited_config_rendered, self.merged_config)
        merge_dicts(self.local_config_rendered, self.merged_config)
        providers = ['parameter', 'secret', 'template']
        
        ### save provider ids before overriding
        saved_provider_ids = {}
        for provider in providers:
            providerId = self.get_provider_id(provider)
            if providerId:
                saved_provider_ids[provider] = providerId
        
        merge_dicts(self.overriden_config, self.merged_config)
        
        ### add missing default specs for each provider
        for provider in providers:
            providerId = self.get_provider_id(provider)
            if providerId:
                ### merge saved spec with the default if only same provider
                if saved_provider_ids.get(provider) == providerId:
                    save = self.get_provider_spec(provider).copy()
                    self.merged_config[provider]['provider']['spec'] = self.get_provider_default_spec(provider, providerId)
                    merge_dicts(save, self.merged_config[provider]['provider']['spec'])
                else:
                    self.merged_config[provider]['provider']['spec'] = self.get_provider_default_spec(provider, providerId)

        self.merged_config['context'] = {
            'namespace': self.namespace,
            'project': self.project,
            'application': self.application,
            'stage': self.short_stage,
            'scope': str(self.scope)
        }

        self.merged_config['stage'] = self.get_stage(ContextSource.Target, short=True)
        self.merged_config['scope'] = str(self.scope)

    def check_version(self):
        if not int(self.merged_config['version']) == int(_default_config['version']):
            if int(self.merged_config['version']) > int(_default_config['version']):
                Logger.warn(MESSAGES['DSOConfigNewer'].format(_default_config['version'], self.merged_config['version']))
            else:
                Logger.warn(MESSAGES['DSOConfigOlder'].format(_default_config['version'], self.merged_config['version']))


    def get_provider_default_spec(self, provider, provider_id):
        if f'{provider}/{provider_id}' in sys.modules:
            provider = sys.modules[f'{provider}/{provider_id}']
        else:
            providerPackagePath = os.path.join(self.install_path, 'provider', f'{provider}/{provider_id}')
            if not os.path.exists(providerPackagePath):
                raise DSOException(f"Provider '{provider}/{provider_id}' not found.")
            provider = imp.load_package(f'{provider}/{provider_id}', providerPackagePath)
        
        return provider.get_default_spec()


    def save_local_config(self):
        os.makedirs(self.local_config_dir_path, exist_ok=True)
        save_data(self.local_config, self.local_config_file_path)

    def save_global_config(self):
        os.makedirs(self.global_config_dir_path, exist_ok=True)
        save_data(self.global_config, self.global_config_file_path)


    @property
    def namespace(self):
        return self.get_namespace()

    def get_namespace(self, source=ContextSource.Effective):
        if source == ContextSource.Target:
            result = self.context.target[0]
        elif source == ContextSource.Effective:
            result = self.context.effective[0]
        
        return result


    @property
    def project(self):
        return self.get_project()

    def get_project(self, source=ContextSource.Effective):
        if source == ContextSource.Target:
            result = self.context.target[1]
        elif source == ContextSource.Effective:
            result = self.context.effective[1]
        
        return result


    @property
    def application(self):
        return self.get_application()


    def get_application(self, source=ContextSource.Effective):
        if source == ContextSource.Target:
            result = self.context.target[2]
        elif source == ContextSource.Effective:
            result = self.context.effective[2]
        
        return result


    @property
    def stage(self):
        return self.get_stage()

    def get_stage(self, source=ContextSource.Effective, short=False):
        if source == ContextSource.Target:
            result = self.context.target[3]
        elif source == ContextSource.Effective:
            result = self.context.effective[3]
        
        if short:
            result = Stages.shorten(result)
        else:
            result = Stages.normalize(result)
        
        return result

    @property
    def short_stage(self):
        return self.get_stage(short=True)


    @property
    def scope(self):
        return self.context.scope


    def get_provider_id(self, provider):
        try:
            result = self.merged_config[provider]['provider']['id'] or os.getenv(f"DSO_{provider.upper()}_PROVIDER_ID")
        except KeyError:
            raise DSOException("Invalid dso configuration schema.")
        return result

    @property
    def parameter_provider(self):
        return self.get_provider_id('parameter')

    # @parameter_provider.setter
    # def parameter_provider(self, value):
    #     self.merged_config['parameter']['provider']['id'] = value

    @property
    def secret_provider(self):
        return self.get_provider_id('secret')

    # @secret_provider.setter
    # def secret_provider(self, value):
    #     self.merged_config['secret']['provider']['id'] = value

    @property
    def template_provider(self):
        return self.get_provider_id('template')

    # @template_provider.setter
    # def template_provider(self, value):
    #     self.merged_config['template']['provider']['id'] = value

    def get_provider_spec(self, provider, key=None):
        try:
            result = self.merged_config[provider]['provider']['spec']
        except KeyError:
            raise DSOException("Invalid dso configuration schema.")
        if not key:
            return result
        elif key in result:
            return result[key]
        else:
            return ''

    def parameter_spec(self, key=None):
        return self.get_provider_spec('parameter', key)


    def secret_spec(self, key=None):
        return self.get_provider_spec('secret', key)


    def template_spec(self, key):
        return self.get_provider_spec('template', key)


    def get_template_render_paths(self, key=None):
        result = get_dict_item(self.local_config, ['template', 'render']) or {}
        if not key:
            return result
        else:
            return {x:result[x] for x in result if x==key}

    def register_template_custom_render_path(self, key, render_path):
        result = get_dict_item(self.local_config, ['template', 'render']) or {}
        # if os.path.isabs(render_path):
        #     raise DSOException(MESSAGES['AbsTemplateRenderPath'].format(render_path))
        # if os.path.isdir(render_path):
        #     raise DSOException(MESSAGES['InvalidRenderPathExistingDir'].format(render_path))
        result[key] = render_path
        self.local_config['template']['render'] = result
        self.save_local_config()

    def unregister_template_custom_render_path(self, key):
        result = get_dict_item(self.local_config, ['template', 'render'])
        if key in result:
            self.local_config['template']['render'].pop(key)
            self.save_local_config()


    def network(self, key=None):
        try:
            result = self.merged_config['network']
        except KeyError:
            raise DSOException("Invalid dso configuration schema.")
        if not key:
            return result
        elif key in result:
            return result[key]
        else:
            return ''

    def get(self, key=None, config_scope=ConfigScope.Merged):
        if key:
            Logger.info("Getting '{0}' from DSO configurations...".format(key))
        else:
            Logger.info("Getting DSO configurations...")

        if config_scope == ConfigScope.Local:
            usedConfig = merge_dicts(self.overriden_config, self.local_config_rendered.copy())
        elif config_scope == ConfigScope.Global:
            usedConfig = merge_dicts(self.overriden_config, self.global_config_rendered.copy())
        else:
            usedConfig = self.merged_config.copy()

        if key:
            result = get_dict_item(usedConfig, key.split('.'))
            if not result:
                raise DSOException(f"DSO configuration '{key}' not found.")
            return result
        else:
            return usedConfig

    def set(self, key, value, config_scope=ConfigScope.Local):
        if config_scope == ConfigScope.Global:
            Logger.info(f"Setting '{key}' to '{value}' in the global DSO configurations...")
            if not os.path.exists(self.global_config_file_path):
                raise DSOException("The global configuration has not been intitialized yet. Run 'dso config init --global' to initialize it.")

            set_dict_value(self.global_config, key.split('.'), value, overwrite_parent=True, overwrite_children=True)
            self.save_global_config()
            self.load_global_config()
            # set_dict_value(self.global_config_rendered, key.split('.'), value, overwrite_parent=True, overwrite_children=True)
            # self.update_merged_config()
        
        elif config_scope == ConfigScope.Local:
            Logger.info(f"Setting '{key}' to '{value}' in the local DSO configurations...")
            if not os.path.exists(self.local_config_file_path):
                raise DSOException("The working directory has not been intitialized yet. Run 'dso config init' to initialize it.")

            set_dict_value(self.local_config, key.split('.'), value, overwrite_parent=True, overwrite_children=True)
            self.save_local_config()
            self.load_local_config()
        else:
            raise NotImplementedError

    def unset(self, key, config_scope=ConfigScope.Local):
        if config_scope == ConfigScope.Global:
            Logger.info(f"Unsetting '{key}' from the global DSO configurations...")
            parent = get_dict_item(self.global_config, key.split('.')[:-1])
            if parent and key.split('.')[-1] in parent:
                parent.pop(key.split('.')[-1])
                self.save_global_config()
                self.load_global_config()
            else:
                raise DSOException(f"'{key}' not found in the global DSO configuratoins.")
        elif config_scope == ConfigScope.Local:
            Logger.info(f"Unsetting '{key}' from the local DSO configurations...")
            parent = get_dict_item(self.local_config, key.split('.')[:-1])
            if parent and key.split('.')[-1] in parent:
                parent.pop(key.split('.')[-1])
                self.save_local_config()
                self.load_local_config()
            else:
                raise DSOException(f"'{key}' not found in the local DSO configuratoins.")
        else:
            raise NotImplementedError

    def init(self, working_dir, custom_init_config, config_overrides_string, override_inherited=False, config_scope=ConfigScope.Local):
        Logger.info("Initializing DSO configurations...")
        self.working_dir = working_dir
        self.local_config_dir_path = os.path.join(self.working_dir, self.config_dir)
        self.local_config_file_path = os.path.join(self.local_config_dir_path, self.config_file)
        self.global_config_dir_path = os.path.join(Path.home(), self.config_dir)
        self.global_config_file_path = os.path.join(self.global_config_dir_path, self.config_file)

        if config_scope == ConfigScope.Local:
            if os.path.exists(self.local_config_file_path):
                Logger.warn("The working directory has already been initialized.")

            config = get_init_config()
            
            ### use init_config instead of local/inherited config
            if custom_init_config:
                merge_dicts(custom_init_config, config)
                ### merge with existing local configuration?
                # if override_inherited:
                #     Logger.debug("Merging local configuration...")
                #     self.load_local_config(silent_warnings=True, render=False)
                #     merge_dicts(self.local_config, config)
                Logger.debug("Merging exisintg configuration...")
                self.load_local_config(silent_warnings=True, render=False)
                merge_dicts(self.local_config, config)
            else:
                ### override locally inherited configuration?
                if override_inherited: 
                    Logger.debug("Merging global configuration...")
                    self.load_global_config(render=False)
                    merge_dicts(self.global_config, config)

                    Logger.debug("Merging inherited configuration...")
                    self.load_inherited_config(render=False)
                    merge_dicts(self.inherited_config_rendered, config)
                
                ### do not show warning if directory is not initialized yet
                Logger.debug("Merging existing configuration...")
                self.load_local_config(silent_warnings=True, render=False)
                merge_dicts(self.local_config, config)

            ### if config overrides, merge them to local
            if config_overrides_string:
                Logger.debug("Merging configuration overrides...")
                self.apply_config_overrides(self.config_string_to_dict(config_overrides_string))
                merge_dicts(self.overriden_config, config)

            self.local_config = config
            self.update_merged_config()

            self.save_local_config()
        
        elif config_scope == ConfigScope.Global:
            if os.path.exists(self.global_config_file_path):
                Logger.warn("The global configuration has already been initialized.")

            config = get_init_config()
            
            ### use init_config instead of local/inherited config
            if custom_init_config:
                merge_dicts(custom_init_config, config)
                ### merge with existing local configuration?
                # if override_inherited:
                #     Logger.debug("Merging local configuration...")
                #     self.load_local_config(silent_warnings=True, render=False)
                #     merge_dicts(self.local_config, config)
                Logger.debug("Merging existing configuration...")
                self.load_global_config(render=False)
                merge_dicts(self.local_global, config)
            else:
                ### do not show warning if directory is not initialized yet
                Logger.debug("Merging existing configuration...")
                self.load_global_config(render=False)
                merge_dicts(self.global_config, config)

            ### if config overrides, merge them to local
            if config_overrides_string:
                Logger.debug("Merging configuration overrides...")
                self.apply_config_overrides(self.config_string_to_dict(config_overrides_string))
                merge_dicts(self.overriden_config, config)

            self.global_config = config
            self.update_merged_config()

            self.save_global_config()

        else:
            raise NotImplementedError




Configs = ConfigService()

