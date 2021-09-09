import os
import re
from .contexts import Contexts
from .logger import Logger
from .stages import Stages
from dsocli.config import Configs
from dsocli.file_utils import *
from dsocli.exceptions import DSOException
from dsocli.dict_utils import *


def encode_local_path(stage, key):
    result = Stages.normalize(stage)
    if key:
        result = os.path.join(result, key)
    return result.replace('/', os.sep)


def decode_local_path(path):
    """
        path is in the form of [/]stage/env_no/[key]
    """
    parts = path.split(os.sep)
    if not parts[0]: parts.pop(0)
    stage = f"{parts[0]}/{parts[1]}"
    key = os.sep.join(parts[2:]) if len(parts) > 2 else None
    return stage, key


def get_local_path(stage, key=None, path_prefix=None):
    return path_prefix + encode_local_path(stage, key)


def get_context_hierachy_local_paths(stage, path_prefix=None, uninherited=False, reverse=False):
    stage = Stages.normalize(stage)
    result = []
    if uninherited:
        result.append(get_local_path(stage=stage, path_prefix=path_prefix))
    else:
        ### Add the application context: /project/application/default/0
        result.append(get_local_path('default/0', path_prefix=path_prefix))
        if not stage is None and not Stages.is_default(stage):
            ### Add the project stage context: /project/application/stage/0
            result.append(get_local_path(Stages.get_default_env(stage), path_prefix=path_prefix))
            ### Add the application numbered stage context: /dso/project/application/stage/env
            if not Stages.is_default_env(stage):
                result.append(get_local_path(stage=stage, path_prefix=path_prefix))

    return list(reversed(result)) if reverse else result


def load_templates_from_path(result, path, stage, include_contents=False, filter=None):
    for pth, subdirs, files in os.walk(path):
        for name in files:
            filePath = os.path.join(pth, name)
            if is_binary_file(filePath): continue
            ### temlate key is the filename stripped out 'path' from the begining
            key = filePath[len(path)+1:].replace(os.sep, '/')
            if filter and not re.match(filter, key): continue
            if key in result:
                Logger.warn(f"Inherited template '{key}' has been overridden.")
            result[key] = {
                'Stage': Stages.shorten(stage),
                'Scope': Contexts.translate_context('project', 'application', stage),
                'Path': filePath[len(Configs.working_dir) + 1:],
                'Date': get_file_modified_date(filePath)
            }
            if include_contents:
                with open(filePath, 'r', encoding='utf-8') as f:
                    result[key]['Contents'] = f.read()

    return result


def load_context_templates(stage, path_prefix=None, uninherited=False, include_contents=False, filter=None):
    ### get templates in normal order (top to bottom)
    paths = get_context_hierachy_local_paths(stage=stage, path_prefix=path_prefix, uninherited=uninherited)
    templates = {}
    for path in paths:
        Logger.debug(f"Loading templates: path={path}")
        load_templates_from_path(result=templates, path=os.path.join(Configs.working_dir, path), stage=decode_local_path(path[len(path_prefix):])[0], include_contents=include_contents, filter=filter)
        # for k in templates: __patch_loaded_template(templates[k], path_prefix)

    return templates


def locate_template_in_context_hierachy(stage, key, path_prefix=None, include_contents=False, uninherited=False):
    templates = {}
    ### get templates in reverse order (more specific to general)
    paths = get_context_hierachy_local_paths(stage=stage, path_prefix=path_prefix, uninherited=uninherited, reverse=True)
    for path in paths:
        load_templates_from_path(result=templates, path=os.path.join(Configs.working_dir, path), stage=decode_local_path(path[len(path_prefix):])[0], include_contents=include_contents, filter=f"^{key}$")
        if key in templates: break

    return templates


def add_local_template(stage, key, path_prefix, contents):
    path = get_local_path(stage=stage, key=key, path_prefix=path_prefix)
    Logger.debug(f"Adding local template: path={path}")
    fullPath = os.path.join(Configs.working_dir, path)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    with open(fullPath, 'w', encoding='utf-8') as f:
        f.write(contents)
    result = {
        'Path': path
    }
    return result


def delete_local_template(path):
    if os.path.exists(path):
        os.remove(path)


def get_parameter_store_path(stage, store_name, path_prefix=None, create=True):
    path = os.path.join(get_local_path(stage=stage, path_prefix=path_prefix), store_name)
    if not os.path.exists(path):
        if create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'w').close()
    return path


def load_parameter_store(result, path, stage, filter=None):
    if not os.path.exists(path): return result
    parameters = flatten_dict(input=load_file(path))
    for key, value in parameters.items():
        if filter and not re.match(filter, key): continue
        if key in result:
            Logger.warn(f"Inherited parameter '{key}' has been overridden.")
        
        result[key] = {
            'Value': value,
            'Path': path,
            'Stage': Stages.shorten(stage),
            'Scope': Contexts.translate_context('project', 'application', stage)

        }

    return result


def get_context_hierachy_parameter_stores(stage, store_name, path_prefix=None, uninherited=False, reverse=False):
    paths = get_context_hierachy_local_paths(stage=stage, path_prefix=path_prefix, uninherited=uninherited, reverse=reverse)
    stores = []
    for path in paths:
        stores.append({
            'Stage': Stages.shorten(decode_local_path(path[len(path_prefix):])[0]),
            'Path': os.path.join(path, store_name)
        })
    return stores


def load_context_local_parameters(stage, store_name, path_prefix=None, uninherited=False, filter=None):
    ### get stores in normal order (top to bottom)
    stores = get_context_hierachy_parameter_stores(stage=stage, store_name=store_name, path_prefix=path_prefix, uninherited=uninherited)
    parameters = {}
    for store in stores:
        Logger.debug(f"Loading store: path={store['Path']}")
        load_parameter_store(result=parameters, path=store['Path'], stage=store['Stage'], filter=filter)

    return parameters


def locate_parameter_in_context_hierachy(stage, key, store_name, path_prefix=None, uninherited=False):
    ### get stores in reverse order (more specific to general)
    stores = get_context_hierachy_parameter_stores(stage=stage, store_name=store_name, path_prefix=path_prefix, uninherited=uninherited, reverse=True)
    parameters = {}
    for store in stores:
        Logger.debug(f"Loading store: path={store['Path']}")
        if os.path.exists(store['Path']):
            load_parameter_store(result=parameters, path=store['Path'], stage=store['Stage'], filter=f"^{key}$")
            if key in parameters: break

    return parameters


def add_local_parameter(stage, key, value, store_name, path_prefix=None):
    path = get_parameter_store_path(stage=stage, store_name=store_name, path_prefix=path_prefix)
    params = load_file(file_path=path)
    set_dict_value(dic=params, keys=key.split('.'), value=value, overwrite_parent=False, overwrite_children=False)
    save_data(data=params, file_path=path)
    result = {
        'Key': key,
        'Value': value,
        'Stage': Stages.shorten(stage),
        'Scope': Contexts.translate_context('project', 'application', stage),
        'Path': path
    }
    return result


def delete_local_parameter(path, key):
    params = load_file(file_path=path)
    del_dict_item(dic=params, keys=key.split('.'))
    del_dict_empty_item(dic=params, keys=key.split('.')[:-1])
    save_data(data=params, file_path=path)

