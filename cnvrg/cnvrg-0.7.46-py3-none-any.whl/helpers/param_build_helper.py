import cnvrg.helpers.apis_helper as apis_helpers
import cnvrg.helpers.config_helper as config_helper
import cnvrg.helpers.env_helper as env_helper
from cnvrg.modules import CnvrgError
import os
## 1
ORGANIZATION = 'ORG'
## 2
PROJECT = 'PRO'
LIBRARY = 'LIBR'
DATASET = 'DATA'
DATA_CONNECTOR = "DATACONNECTOR"
## 3
EXPERIMENT = 'EXP'
NOTEBOOK = 'NOTE'
ENDPOINT = 'ENDP'
FLOW = 'FLOW'
## 4
TAG = 'TAG'
DEPLOYMENT = 'DEPL'


def type_to_depth(d_type):
    if d_type in [ORGANIZATION]: return 1
    if d_type in [PROJECT, DATASET, LIBRARY, DATA_CONNECTOR]: return 2
    if d_type in [EXPERIMENT, NOTEBOOK, ENDPOINT, FLOW]: return 3
    if d_type in [TAG, DEPLOYMENT]: return 4


def min_params(d_type):
    if d_type in [LIBRARY]: return 1
    return 0

def parse_params(params, type=None, working_dir=None):
    working_dir = working_dir or os.curdir
    num_of_params = len(params.split("/")) if params else 0
    if num_of_params < min_params(type):
        raise CnvrgError("Expecting {min_params} params".format(min_params=min_params(type)))
    splitted = params.split("/") if params else []
    if num_of_params == type_to_depth(type):
        return [*splitted]
    if num_of_params == type_to_depth(type) - 1:
        ## assuming logged in
        return [apis_helpers.credentials.owner, *splitted]
    if num_of_params == type_to_depth(type) - 2:
        ### assuming in project
        element = config_helper.get_element_slug(working_dir)
        owner = config_helper.get_element_owner(working_dir)
        return [owner, element, *splitted]
    if num_of_params == type_to_depth(type) - 3:
        current_job_slug = env_helper.get_current_job_id()
        project_slug = config_helper.get_element_slug(working_dir)
        owner = config_helper.get_element_owner(working_dir)
        return [owner, project_slug, current_job_slug]

