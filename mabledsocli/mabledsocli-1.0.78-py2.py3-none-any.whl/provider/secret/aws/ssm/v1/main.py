import boto3
from mabledsocli.exceptions import DSOException
from mabledsocli.logger import Logger
from mabledsocli.providers import Providers
from mabledsocli.secrets import SecretProvider
from mabledsocli.stages import Stages
from mabledsocli.constants import *
from mabledsocli.dict_utils import set_dict_value
from mabledsocli.contexts import Contexts
from mabledsocli.aws_utils import *


__default_spec = {
    'path': '/dso/v1/secrets',
    # 'namnespace': 'default',
}

def get_default_spec():
    return __default_spec.copy()


class AwsSsmSecretProvider(SecretProvider):


    def __init__(self):
        super().__init__('secret/aws/ssm/v1')


    def get_path_prefix(self):
        return self.config.secret_spec('path')


    def list(self, config, uninherited=False, decrypt=False, filter=None):
        self.config = config
        secrets = load_context_ssm_parameters(config=config, parameter_type='SecureString', path_prefix=self.get_path_prefix(), uninherited=uninherited, decrypt=decrypt, filter=filter)
        result = {'Secrets': []}
        for key, details in secrets.items():
            item = {
                'Key': key,
                'RevisionId': str(details['Version']),
            }
            item.update(details)
            result['Secrets'].append(item)

        return result



    def add(self, config, key, value):
        self.config = config
        Logger.debug(f"Checking SSM secret overwrites '{key}': namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        assert_ssm_parameter_no_namespace_overwrites(config=config, key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Locating SSM secret '{key}': namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if found and not found['Type'] == 'SecureString':
            raise DSOException(f"Failed to add secret '{key}' becasue becasue the key is not available in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        path = get_ssm_path(context=config.context, key=key, path_prefix=self.get_path_prefix())
        Logger.debug(f"Adding SSM secret: path={path}")
        response = put_ssm_secret(path, value)
        result = {
                'RevisionId': str(response['Version']),
                'Key': key, 
                'Value': value,
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


    def get(self, config, key, decrypt=False, revision=None):
        self.config = config
        Logger.debug(f"Locating SSM secret '{key}': namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix())
        if not found:
            raise DSOException(f"Secret '{key}' not found nor inherited in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        else:
            if not found['Type'] == 'SecureString':
                raise DSOException(f"Parameter '{key}' not found in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        Logger.debug(f"Getting SSM secret: path={found['Name']}")
        response = get_ssm_secret_history(found['Name'], decrypt)
        secrets = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if revision is None:
            ### get the latest revision
            result = {
                    'RevisionId': str(secrets[0]['Version']),
                    'Date': secrets[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': secrets[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': secrets[0]['LastModifiedUser'],
                    }

        else:
            ### get specific revision
            secrets = [x for x in secrets if str(x['Version']) == revision]
            if not secrets:
                raise DSOException(f"Revision '{revision}' not found for secret '{key}' in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
            result = {
                    'RevisionId': str(secrets[0]['Version']),
                    'Date': secrets[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': secrets[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': secrets[0]['LastModifiedUser'],
                    }

        return result



    def history(self, config, key, decrypt=False):
        self.config = config
        Logger.debug(f"Locating SSM secret '{key}': project={config.project}, application={config.application}, stage={config.stage}")
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix())
        if not found:
            raise DSOException(f"Secret '{key}' not found in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        else:
            if not found['Type'] == 'SecureString':
                raise DSOException(f"Parameter '{key}' not found in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        Logger.debug(f"Getting SSM secret: path={found['Name']}")
        response = get_ssm_secret_history(found['Name'], decrypt)
        secrets = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        result = { "Revisions":
            [{
                'RevisionId': str(secret['Version']),
                'Date': secret['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                'Key': key,
                'Value': secret['Value'],
                # 'Scope': found['Scope'],
                # 'Origin': found['Origin'],
                'User': secret['LastModifiedUser'],
                # 'Path': found['Name'],
            } for secret in secrets]
        }

        return result



    def delete(self, config, key):
        self.config = config
        Logger.debug(f"Locating SSM secret '{key}': namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.stage}")
        ### only secrets owned by the context can be deleted, hence uninherited=True
        found = locate_ssm_parameter_in_context_hierachy(config=config, key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
                raise DSOException(f"Secret '{key}' not found in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        else:
            # if len(found) > 1:
            #     Logger.warn(f"More than one secret found at '{found['Name']}'. The first one taken, and the rest were discarded.")
            if not found['Type'] == 'SecureString':
                raise DSOException(f"Secret '{key}' not found in the given context: namespace={config.namespace}, project={config.project}, application={config.application}, stage={config.short_stage}")
        Logger.debug(f"Deleting SSM secret: path={found['Name']}")
        delete_ssm_parameter(found['Name'])
        return {
                'Key': key,
                'Stage': found['Stage'],
                'Scope': found['Scope'],
                'Origin': found['Origin'],
                'Path': found['Name'],
                }



def register():
    Providers.register(AwsSsmSecretProvider())
