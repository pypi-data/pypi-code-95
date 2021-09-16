import os
import requests
import json
import pyhectiqlab.settings as settings
import threading
import logging
import time
from typing import List
from more_itertools import chunked

from pyhectiqlab.upload import upload_file

logger = logging.getLogger('hectiqlab')

def lab_request(path, request_type, form_data=None, query_args=None, body_args=None, token=None):

    if path.startswith('http://') or path.startswith('https://'):
        url = path
    else:
        url = settings.server_url + path
    if query_args:
        url += "?"
        for key, val in query_args.items():
            if val is not None:
                url += f"{key}={val}&"

    headers = {}
    if token:
        headers = {"X-API-Key": f"{token}"}
    body = None
    if body_args:
        body = json.dumps(body_args)
    files = None
    if form_data:
        body = form_data
        headers["content-type"] = 'application/x-www-form-urlencoded'
    if request_type=="GET":
        call = requests.get
    elif request_type=="PUT":
        call = requests.put
    elif request_type=="POST":
        call = requests.post
    try:
        res = call(url, data=body, headers=headers, files=files)
        logger.debug('LABREQUEST:')
        logger.debug(url)
        logger.debug(res.status_code)
        if res.status_code==401:
            logger.debug(res.json()["detail"])
            return {"status_code": 401, "detail": res.json().get("detail")}
        else:
            data = res.json()
            logger.debug(res.json())
            if isinstance(data, list):
                data = {"result": data}
            data["status_code"] = res.status_code
            return data
    except:
        return {"status_code": 400}


def fetch_secret_api_token(username, password):
    res = lab_request(path="/generate_secret_api_token", 
                request_type="POST", 
                form_data=dict(username=username, password=password))
    return res

def update_secret_api_token_name(api_key_uuid, name, token):
    res = lab_request(path=f"/api-key/{api_key_uuid}", 
                request_type="PUT", 
                token=token,
                body_args=dict(name=name))
    return res

def fetch_minimum_python_version():
    res = lab_request(path="/minimum-supported-python-version", 
                request_type="GET")
    return res

def create_project(name, force_create, token):
    res = lab_request(path="/projects/", 
                request_type="POST", 
                token=token,
                body_args=dict(name=name, force_create=force_create))
    return res

def list_shared_artifacts(project_id, token):
    res = lab_request(path="/artifacts/shared", 
                request_type="GET", 
                token=token,
                query_args=dict(project_id=project_id))
    return res

def get_artifact_signed_url(artifact_uuid, token):
    res = lab_request(path=f"/artifacts/url", 
                request_type="GET", 
                token=token,
                query_args=dict(artifact_uuid=artifact_uuid))
    return res

def create_run(name, project_name, token):
    res = lab_request(path="/runs/", 
                request_type="POST", 
                token=token,
                body_args=dict(name=name, project_name=project_name))
    return res

def get_existing_run_info(run_id, token):
    res = lab_request(path=f"/runs/{run_id}", 
                request_type="GET", 
                token=token)
    return res

def push_metrics(run_id, metrics_name, values, token):
    res = lab_request(path=f"/metrics/{run_id}/add",
                     request_type="POST",
                     token=token,
                     body_args=dict(name=metrics_name, values=values))
    return res

def set_run_status(run_id, status, token):
    res = lab_request(path=f"/runs/{run_id}/status",
                     request_type="POST",
                     token=token,
                     body_args=dict(status=status))
    return res

def push_meta(run_id, key, value, token):
    res = lab_request(path=f"/runs/{run_id}/meta",
                     request_type="POST",
                     token=token,
                     body_args=dict(meta={key:value}))
    return res

def push_package_versions(run_id, data, token):
    res = lab_request(path=f"/runs/{run_id}/packages",
                     request_type="POST",
                     token=token,
                     body_args=dict(packages=data))
    return res

def push_git_package_state(run_id, data, token):
    res = lab_request(path=f"/runs/{run_id}/git_package_meta",
                     request_type="POST",
                     token=token,
                     body_args=dict(gitmeta=data))
    return res

def set_note(run_id, note, token):
    res = lab_request(path=f"/runs/{run_id}/comment",
                     request_type="POST",
                     token=token,
                     body_args=dict(text=note))
    return res

def set_paper(run_id, content, token):
    res = lab_request(path=f"/runs/{run_id}/paper",
                     request_type="POST",
                     token=token,
                     body_args=dict(source=content))
    return res

def add_tag(run_id, name, description, color, token):
    res = lab_request(path=f"/runs/{run_id}/tags",
                     request_type="POST",
                     token=token,
                     body_args=dict(tag_name=name, tag_description=description, tag_color=color, can_remove=False))
    return res

def log_mlmodel(run_id, mlmodel_name, version, project_id, token):
    res = lab_request(path=f"/runs/{run_id}/log_mlmodel",
                     request_type="POST",
                     token=token,
                     query_args=dict(mlmodel_name=mlmodel_name, version=version, project_id=project_id))
    return res

def log_dataset(run_id, dataset_name, version, project_id, token):
    res = lab_request(path=f"/runs/{run_id}/log_dataset",
                     request_type="POST",
                     token=token,
                     query_args=dict(dataset_name=dataset_name, version=version, project_id=project_id))
    return res

def append_logs(run_id, logs, token):
    if logs is None:
        return
    res = lab_request(path=f"/runs/{run_id}/logs",
                     request_type="POST",
                     token=token,
                     body_args=dict(logs=logs))
    return res

def add_artifact(run_id, filename: str, filepath: str, num_bytes: int = None, step: int = None, token: str = None):

    # Get policy
    args = dict(run_id=run_id, filename=filename)
    if step is not None:
        args['step'] = step
    if num_bytes:
        args["num_bytes"] = num_bytes
    res = lab_request(path=f"/runs/{run_id}/file_policy",
                     request_type="GET",
                     token=token,
                     query_args=args)
    try:
        logger.debug('ops.add_artifacts:: Upload starting.')

        callback_url = res.get('callback_url')
        upload_file(filepath, res)
        logger.debug('ops.add_artifacts:: Upload completed.')
        # Callback
        logger.debug(f'ops.add_artifacts:: Send callback at {callback_url}')
        res = lab_request(callback_url,
                     request_type="GET",
                     token=token)
        return res
    except:
        # Unable
        print(f'Unable to push artifact {filepath}.')
        return res

def get_mlmodel_download_info(mlmodel_name, project_id, version, token):
    res = lab_request(path=f"/mlmodels/download_info/",
                     request_type="GET",
                     token=token,
                     query_args=dict(mlmodel_name=mlmodel_name, project_id=project_id, version=version))
    return res

def get_dataset_download_info(dataset_name, project_id, version, token):
    res = lab_request(path=f"/datasets/download_info/",
                     request_type="GET",
                     token=token,
                     query_args=dict(dataset_name=dataset_name, project_id=project_id, version=version))
    return res

def add_mlmodel(run_id, filenames: List[str], full_paths: List[str], num_bytes: List[int], name: str, short_description: str, version: str, token: str = None):

    # Get policy
    body = dict(run_id=run_id, name=name, filenames=filenames, 
        short_description=short_description, 
        num_bytes=num_bytes, 
        version=version)

    res = lab_request(path=f"/runs/{run_id}/mlmodel",
                     request_type="POST",
                     token=token,
                     body_args=body)
    if res.get('status_code') == 400:
        print(res.get('detail'))
        return

    mlmodel = res.get('mlmodel')
    for filename, policy in res['policies'].items():
        print(f'Uploading {filename}')
        if filename is None:
            continue

        upload_file(full_paths[filename], policy)

        # Callback
        callback_url = policy.get('callback_url')
        lab_request(callback_url,
                     request_type="GET",
                     token=token)
    return mlmodel

def add_dataset(run_id, filenames: List[str], full_paths: List[str], num_bytes: List[int], name: str, short_description: str, version: str, token: str = None):

    # Create dataset
    body = dict(run_id=run_id, name=name, filenames=[], 
            short_description=short_description, 
            num_bytes=[], 
            version=version)
    res = lab_request(path=f"/runs/{run_id}/dataset",
                         request_type="POST",
                         token=token,
                         body_args=body)
    assert res.get('status_code') == 200, f"An error occured while creating the dataset: {res.get('detail')}"
    dataset = res.get('dataset')
    print(f"Creating dataset {dataset.get('name')}, version {dataset.get('version')}.")

    batch_size = 20 # Number of elements to send
    for batch in chunked(zip(filenames, full_paths, num_bytes), batch_size):
        batch_filenames = list(zip(*batch))[0]
        batch_full_paths = list(zip(*batch))[1]
        batch_num_bytes = list(zip(*batch))[2]

        # Get policy
        body = dict(run_id=run_id, filenames=batch_filenames, 
            num_bytes=batch_num_bytes)

        res = lab_request(path=f"/runs/{run_id}/add-files-to-dataset",
                         request_type="POST",
                         token=token,
                         query_args=dict(dataset_uuid=dataset.get('uuid')),
                         body_args=body)
        assert res.get('status_code') == 200, f"An error occured while pushing new files: {res.get('detail')}"

        for filename, policy in res['policies'].items():
            print(f'Uploading {filename}')
            if filename is None:
                continue

            upload_file(full_paths[filename], policy)

            # Callback
            callback_url = policy.get('callback_url')
            lab_request(callback_url,
                         request_type="GET",
                         token=token)
    return dataset


def add_shared_artifact(project_id: str, filename: str, filepath: str, num_bytes: int, token: str = None):

    # Get policy
    args = dict(project_id=project_id, filename=filename, num_bytes=num_bytes)
    res = lab_request(path=f"/artifacts/shared",
                     request_type="POST",
                     token=token,
                     query_args=args)
    try:
        upload_file(filepath, res)

        # Callback
        callback_url = res.get('callback_url')
        lab_request(callback_url,
                     request_type="GET",
                     token=token)
        return res
    except:
        # Unable
        print('Unable to upload file')
        return res

def get_shared_artifacts_download_link(artifact_uuid, token):
    res = lab_request(path=f"/artifacts/url",
                     request_type="GET",
                     token=token,
                     query_args=dict(artifact_uuid=artifact_uuid))
    return res

def get_all_projects(token):
    res = lab_request(path=f"/projects/all",
                     request_type="GET",
                     token=token)
    return res