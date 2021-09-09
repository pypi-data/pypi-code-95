import os
from dsocli.logger import Logger
from dsocli.config import Configs
from dsocli.providers import Providers
from dsocli.parameters import ParameterProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.exceptions import DSOException
from dsocli.contexts import Contexts
from dsocli.local_utils import *
from dsocli.settings import *


_default_spec = {
    'path': os.path.join(Configs.config_dir, 'parameters'),
    'store': 'local.yaml',
}


def get_default_spec():
    return _default_spec.copy()



class LocalParameterProvider(ParameterProvider):

    def __init__(self):
        super().__init__('parameter/local/v1')

    @property
    def root_dir(self):
        return Configs.parameter_spec('path')


    def get_path_prefix(self):
        return self.root_dir + os.sep

    @property
    def store_name(self):
        return Configs.parameter_spec('store')

 
    def add(self, project, application, stage, key, value):
        Logger.debug(f"Adding local parameter: stage={stage}, key={key}")
        response = add_local_parameter(stage, key, value, store_name=self.store_name, path_prefix=self.get_path_prefix())
        return response


    def list(self, project, application, stage, uninherited=False, filter=None):
        parameters = load_context_local_parameters(stage, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=uninherited, filter=filter)
        result = {'Parameters': []}
        for key, details in parameters.items():
            item = {
                'Key': key,
            }
            item.update(details)
            result['Parameters'].append(item)

        return result



    def get(self, project, application, stage, key, revision=None):
        if revision:
            raise DSOException(f"Parameter provider 'local/v1' does not support versioning.")
        Logger.debug(f"Getting parameter: stage={stage}, key={key}")
        found = locate_parameter_in_context_hierachy(stage=stage, key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=False)
        if not found:
            raise DSOException(f"Parameter '{key}' not found nor inherited in the given context: stage={Stages.shorten(stage)}")
        result = {
                'Key': key, 
            }
        result.update(found[key])
        return result



    def delete(self, project, application, stage, key):
        Logger.debug(f"Locating parameter: stage={stage}, key={key}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_parameter_in_context_hierachy(stage=stage, key=key, store_name=self.store_name, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: stage={Stages.shorten(stage)}")
        Logger.info(f"Deleting parameter: path={found[key]['Path']}")
        delete_local_parameter(found[key]['Path'], key=key)
        result = {
                'Key': key,
                'Stage': Stages.shorten(stage),
                'Path': found[key]['Path'],
            }
        return result



def register():
    Providers.register(LocalParameterProvider())
