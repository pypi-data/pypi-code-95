
import os
import re
import jinja2
from jinja2 import meta
from .constants import *
from .providers import StoreProvider, Providers
from .parameters import Parameters
from .secrets import Secrets
from .logger import Logger
from .dict_utils import merge_dicts, deflatten_dict
from .exceptions import DSOException
from .stages import Stages
from .config import ContextSource


REGEX_PATTERN = r"^[a-zA-Z]([./a-zA-Z0-9_-]*[a-zA-Z0-9])?$"

class TemplateProvider(StoreProvider):
    def list(self, config, uninherited=False, include_contents=False, filter=None):
        raise NotImplementedError()
    def add(self, config, key, contents, render_path):
        raise NotImplementedError()
    def get(self, config, key, revision=None):
        raise NotImplementedError()
    def history(self, config, key, include_contents=False):
        raise NotImplementedError()
    def delete(self, config, key):
        raise NotImplementedError()


class TemplateService():
    
    @property
    def default_render_path(self):
        return self.config.working_dir

    def validate_key(self, key):
        Logger.info(f"Validating template key '{key}'...")
        if not key:
            raise DSOException(MESSAGES['KeyNull'])
        if key == 'dso' or key.startswith('dso.'):
            raise DSOException(MESSAGES['DSOReserverdKey'].format(key))
        if not re.match(REGEX_PATTERN, key):
            raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, REGEX_PATTERN))
        ### the regex does not check adjacent special chars
        if '..' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '..'))

        if '//' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '//'))

    def get_template_render_path(self, key):
        result = self.config.get_template_render_paths(key)
        if result:
            return result[key]

        return f'.{os.sep}' + os.path.relpath(os.path.join(Templates.default_render_path, key), self.config.working_dir) 

    def list(self, config, uninherited=False, include_contents=False, filter=None):
        self.config = config
        provider = Providers.TemplateProvider()
        Logger.info(f"Start listing templates: namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)} application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        response = provider.list(config, uninherited, include_contents, filter)
        for template in response['Templates']:
            key = template['Key']
            template['RenderPath'] = self.get_template_render_path(key)
        
        return response

    def add(self, config, key, contents, render_path):
        self.validate_key(key)
        self.config = config
        provider = Providers.TemplateProvider()
        Logger.info(f"Start adding template '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)} application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        Logger.debug(f"Template: key={key}, render_path={render_path}")
        result = provider.add(config, key, contents)
        result['RenderPath'] = render_path
        if os.path.abspath(render_path) == os.path.abspath(os.path.join(self.default_render_path, key)):
            config.unregister_template_custom_render_path(key)
        else:
            config.register_template_custom_render_path(key, render_path)
        return result

    def get(self, config, key, revision=None):
        self.config = config
        provider = Providers.TemplateProvider()
        Logger.info(f"Start getting template '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)} application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        result = provider.get(config, key, revision)
        result['RenderPath'] = self.get_template_render_path(key)
        return result

    def history(self, config, key, include_contents=False):
        self.config = config
        provider = Providers.TemplateProvider()
        Logger.info(f"Start getting the history of template '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)} application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        return provider.history(config, key, include_contents)

    def delete(self, config, key):
        self.config = config
        provider = Providers.TemplateProvider()
        Logger.info(f"Start deleting template '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)} application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        result = provider.delete(config, key)
        config.unregister_template_custom_render_path(key)
        return result

    def render(self, config, filter=None):
        self.config = config

        Logger.info(f"Start rendering templates: namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)} application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")

        Logger.info("Loading secrets...")
        secrets = Secrets.list(config, uninherited=False, decrypt=True)

        Logger.info("Loading parameters...")
        parameters = Parameters.list(config, uninherited=False)

        Logger.info("Merging all parameters...")
        merged = deflatten_dict({x['Key']: x['Value'] for x in secrets['Secrets']})
        merge_dicts(deflatten_dict({x['Key']: x['Value'] for x in parameters['Parameters']}), merged)
        merge_dicts(config.meta_vars, merged)

        Logger.info("Loading templates...")
        templates = self.list(config, filter=filter)['Templates']

        loader = jinja2.FileSystemLoader(config.working_dir)
        jinja_env = jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)

        rendered = []
        if len(templates) == 0:
            Logger.warn("No template found to render.")
            return rendered

        Logger.info("Rendering templates...")
        for template in templates:
            key = template['Key']

            renderPath = template['RenderPath']
            if os.path.isdir(renderPath):
                raise DSOException("There is an existing directory at the template render path '{renderPath}'.")
            if os.path.dirname(renderPath):
                os.makedirs(os.path.dirname(renderPath), exist_ok=True)

            try:
                jinjaTemplate = jinja_env.from_string(self.get(config, key)['Contents'])
            except:
                Logger.error(f"Failed to load template: {key}")
                raise
            # undeclaredParams = jinja2.meta.find_undeclared_variables(env.parse(template))
            # if len(undeclaredParams) > 0:
            #     Logger.warn(f"Undecalared parameter(s) found:\n{set(undeclaredParams)}")
            try:
                Logger.debug(f"Rendering template: key={key}, render_path={renderPath}")
                if len(loader.searchpath) > 1: loader.searchpath.pop(-1)
                loader.searchpath.append(os.path.dirname(os.path.join(config.working_dir, renderPath)))
                renderedContent = jinjaTemplate.render(merged)
            
            except Exception as e:
                Logger.error(f"Failed to render template: {key}")
                msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
                raise DSOException(msg)

            with open(renderPath, 'w', encoding='utf-8') as f:
                f.write(renderedContent)
            
            rendered.append({
                        'Key':key, 
                        'Scope': template['Scope'],
                        # 'Origin': template['Origin'],
                        'RenderPath': renderPath,
                        })

        return rendered


Templates = TemplateService()