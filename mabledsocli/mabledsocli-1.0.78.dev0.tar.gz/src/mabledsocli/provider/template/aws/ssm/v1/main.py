import boto3
from mabledsocli.exceptions import DSOException
from mabledsocli.logger import Logger
from mabledsocli.providers import Providers
from mabledsocli.templates import TemplateProvider
from mabledsocli.stages import Stages
from mabledsocli.constants import *
from mabledsocli.dict_utils import set_dict_value
from mabledsocli.contexts import Contexts
from mabledsocli.aws_utils import *
from mabledsocli.settings import *


__default_spec = {
    'path': '/dso/v1/templates',
    # 'namnespace': 'default',
}

def get_default_spec():
    return __default_spec.copy()


class AwsSsmTemplateProvider(TemplateProvider):


    def __init__(self):
        super().__init__('template/aws/ssm/v1')


    def get_path_prefix(self):
        return self.config.template_spec('path')


    def list(self, config, uninherited=False, include_contents=False, filter=None):
        self.config = config
        templates = load_context_ssm_parameters(config=config, parameter_type='StringList', path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = {'Templates': []}
        for key, details in templates.items():
            item = {
                'Key': key,
                'RevisionId': str(details['Version']),
            }
            item.update(details)
            if include_contents: item['Contents'] = item['Value']
            item.pop('Value')
            result['Templates'].append(item)
        return result


    def add(self, config, key, contents, render_path=None):
        self.config = config
        if len(contents) > 4096:
            raise DSOException(f"This template provider does not support templates larger than 4KB.")
        if not Stages.is_default(config.stage) and not ALLOW_STAGE_TEMPLATES:
            raise DSOException(f"Templates may not be added to stage scopes, as the feature is currently disabled. It may be enabled by adding 'ALLOW_STAGE_TEMPLATES=yes' to the DSO global settings, or adding environment variable 'DSO_ALLOW_STAGE_TEMPLATES=yes'.")
        Logger.debug(f"Checking SSM template '{key}' overwrites: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        assert_ssm_parameter_no_namespace_overwrites(config=config, key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Locating SSM template '{key}': namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if found and not found['Type'] == 'StringList':
            raise DSOException(f"Failed to add template '{key}' becasue becasue the key is not available in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        path = get_ssm_path(context=config.context, key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Adding SSM template: path={path}")
        response = put_ssm_template(path, contents)
        result = {
                'RevisionId': str(response['Version']),
                'Key': key,
                'Stage': config.short_stage,
                'Scope': config.context.scope_translation,
                'Origin': {
                    'Namespace': config.namespace,
                    'Project': config.project,
                    'Application': config.application,
                    'Stage': config.stage,
                },
                'Path': path,
            }
        result.update(response)
        return result


    def get(self, config, key, revision=None):
        self.config = config
        Logger.debug(f"Locating SSM template '{key}': namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix())
        if not found:
            raise DSOException(f"Template '{key}' not found nor inherited in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        else:
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        Logger.debug(f"Getting SSM template: path={found['Name']}")
        response = get_ssm_template_history(found['Name'])
        templates = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if revision is None:
            ### get the latest revision
            result = {
                    'RevisionId': str(templates[0]['Version']),
                    'Date': templates[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'User': templates[0]['LastModifiedUser'],
                    'Path': found['Name'],
                    'Contents': templates[0]['Value'],
                    }
        else:
            ### get specific revision
            templates = [x for x in templates if str(x['Version']) == revision]
            if not templates:
                raise DSOException(f"Revision '{revision}' not found for template '{key}' in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
            result = {
                    'RevisionId': str(templates[0]['Version']),
                    'Date': templates[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': templates[0]['LastModifiedUser'],
                    'Contents': templates[0]['Value'],
                    }

        return result



    def history(self, config, key, include_contents=False):
        self.config = config
        Logger.debug(f"Locating SSM template '{key}': namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix())
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        else:
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        Logger.debug(f"Getting SSM template: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        templates = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if include_contents:
            result = { "Revisions":
                [{
                    'RevisionId': str(template['Version']),
                    'Date': template['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Origin': found['Origin'],
                    'User': template['LastModifiedUser'],
                    # 'Path': found['Name'],
                    'Contents': templates[0]['Value'],

                } for template in templates]
            }
        else:
            result = { "Revisions":
                [{
                    'RevisionId': str(template['Version']),
                    'Date': template['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Origin': found['Origin'],
                    'User': template['LastModifiedUser'],
                    # 'Path': found['Name'],
                } for template in templates]
            }

        return result



    def delete(self, config, key):
        self.config = config
        Logger.debug(f"Locating SSM template '{key}': namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        else:
            # if len(found) > 1:
            #     Logger.warn(f"More than one template found at '{found['Name']}'. The first one taken, and the rest were discarded.")
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: namespace:{config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        Logger.debug(f"Deleting SSM template: path={found['Name']}")
        delete_ssm_parameter(found['Name'])
        return {
                'Key': key, 
                'Stage': found['Stage'],
                'Scope': found['Scope'],
                'Origin': found['Origin'],
                'Path': found['Name'],
                }



def register():
    Providers.register(AwsSsmTemplateProvider())
