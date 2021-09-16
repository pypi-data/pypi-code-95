import os
from pyhectiqlab.utils import get_single_user_project, list_all_files_in_dir, load_event_manager

import requests
from tqdm import tqdm
import logging
import json
import datetime as dt
import packaging.version as pack_version

logger = logging.getLogger('pyhectiqlab')
logger.setLevel(logging.WARNING)

def dataset_info_at_path(dirpath: str):
    try:
        with open(os.path.join(dirpath, '.hlab_meta.json'), "r") as f:
            data = json.load(f)
        return data
    except:
        return None

def upload_dataset(source_path: str, dataset_name: str, run_id: str = None, version: str = None,
    short_description: str = None, push_dir:bool = False):
    assert ' ' not in dataset_name, f"The name cannot contain spaces (use `{dataset_name.replace(' ','-')}`)"
    assert '/' not in dataset_name, f"The name cannot contain / (use `{dataset_name.replace('/','-')}`)"

    manager = load_event_manager()

    if version is not None:
        v = pack_version.parse(version)
        assert isinstance(v, pack_version.Version), 'Cannot use legacy version names. Use a format major.minor.micro.'
        updated_version = f'{v.major}.{v.minor}.{v.micro}'
        assert updated_version==version, f'Please change version to {updated_version}.'

    if os.path.isdir(source_path):
        print('The dataset is a directory. Listing all files...')
        paths = list_all_files_in_dir(source_path)
        filenames = [os.path.relpath(p, start=source_path) for p in paths]
        num_bytes = [os.path.getsize(p) for p in paths]
        full_paths = {f: os.path.abspath(p) for f,p in zip(filenames, paths)}
        print(f'Found {len(filenames)} files')

        assert push_dir, 'Set push_dir=True to push a directory.'

    else:
        filenames = [os.path.basename(source_path)]
        full_paths = {os.path.basename(source_path): os.path.abspath(source_path)}
        num_bytes = [os.path.getsize(source_path)]
    args = (run_id, filenames, full_paths, num_bytes, dataset_name, short_description, version)
    return manager.add_event("add_dataset", args, async_method=False)

def download_dataset(dataset_name: str, project_id: str = None, version: str = None, 
    save_path: str = './', overwrite: bool = False):

    if project_id is None:
        project = get_single_user_project()
        if project is None:
            logger.error('Cannot download dataset without a specific project.')
            return
        project_id = project.get('id')

    manager = load_event_manager()
    if version is not None:
        dirpath = os.path.join(save_path, dataset_name+'-'+version)
        if os.path.isdir(dirpath) and overwrite==False:
            logger.error(f'Dataset is already downloaded at {dirpath}. Delete this folder or set overwrite==True to download again.')
            return dirpath
            
    # Fetch the download info
    res = manager.add_event('get_dataset_download_info', 
            args=(dataset_name, project_id, version), 
            async_method=False)

    assert res.get('status_code')==200, res.get('detail')
    downloaded_version = res.get('meta').get('version')

    dirpath = os.path.join(save_path, dataset_name+'-'+downloaded_version)

    if version is None:
        logger.info(f'Fetching version {downloaded_version}')

    if os.path.isdir(dirpath) and overwrite==False:
        logger.error(f'Dataset is already downloaded at {dirpath}. Delete this folder or set overwrite==True to download again.')
        return dirpath

    if os.path.isdir(dirpath)==False:
        os.makedirs(dirpath)

    meta = res.get('meta')
    text = f"{meta.get('name')}\nVersion: {meta.get('version')}\nProject: {project_id}\n"
    text += f"UUID: {meta.get('uuid')}\nDescription: {meta.get('description')}\n"
    text += f"Downloaded on: {dt.datetime.now()}"
    text += '\n--------------------------\n'
    if meta.get('full_description'):
        text += meta.get('full_description')
    else:
        text += 'No description.'
    with open(os.path.join(dirpath, 'HLab_README.md'), "w") as f:
        f.write(text)

    with open(os.path.join(dirpath, '.hlab_meta.json'), "w") as f:
        json.dump(meta, f)

    # Download the files
    files = res.get('files')
    logger.info(f'Downloading {len(files)} files')
    for file_meta in files:
        url = file_meta['url']
        name = file_meta['name']
        if os.path.dirname(name)!='':
            subdirpath = os.path.join(dirpath, os.path.dirname(name))
            if os.path.isdir(subdirpath) == False:
                os.makedirs(subdirpath)
        logger.info(name)
        response = requests.get(url, stream=True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        path = os.path.join(dirpath, name)
        with open(path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            logger.error("ERROR, something went wrong when downloading the file.")
        
        logger.info(f'Content saved at {path}')
    return dirpath
