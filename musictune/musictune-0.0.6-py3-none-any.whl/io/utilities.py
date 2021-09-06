import glob
import json
import math
import os
from ast import literal_eval

import dask.array as da
import pkg_resources
import zarr


def read_config(config_path, session_to_process=None, lasers_to_process=None, pzf_dirs_to_process=None):
    f = open(config_path, "r")
    config = json.loads(f.read())
    f.close()

    root_dir = os.path.dirname(config_path)
    no_of_sessions = len(config['Sessions'])

    stp = range(*(session_format(session_to_process)).indices(no_of_sessions))

    sessions = {}
    idx = 0
    for s in stp:
        sessions[idx] = {}
        print(f'Imaging session: {s}')
        session = config['Sessions'][s]
        s_id = session['Session']
        s_dir = os.path.join(root_dir, s_id)

        lasers = session['Laser Sequence']
        print(f'\tFound laser sequences: {lasers}')

        ll = laser_format(lasers_to_process)
        ltp = ll if ll else lasers

        sessions[idx]['Files'] = {}
        for l in ltp:
            files = sorted(glob.glob(os.path.join(s_dir, f"*{l}*")))
            pzf_dir = list(filter(os.path.isdir, files))
            print(f'\t{l}: {len(pzf_dir)} Blocks with {len(os.listdir(pzf_dir[0]))} planes')
            sessions[s]['Files'][l] = pzf_dir[pzf_dir_format(pzf_dirs_to_process)]

        sessions[idx]['Image Start'] = session['YScan']['Image Start']
        sessions[idx]['Image End'] = session['YScan']['Image End']
        sessions[idx]['Pixel Size'] = session['YScan']['Pixel Size']
        sessions[idx]['Scale Factor'] = session['YScan']['Scale Factor']

        is_reversed = session['ZScan']['Z Increment'] < 0

        img_res_y = 1e6 * session['YScan']['Pixel Size'] * session['YScan']['Scale Factor']
        img_res_z = 1e6 * session['ZScan']['Z Increment']

        sessions[idx]['Image Resolution'] = (abs(img_res_z), 0.23325, img_res_y)
        sessions[idx]['Reversed'] = is_reversed

        overlap = round(2048 - abs(1e6 * session['XScan']['X Increment']) / 0.23325)
        sessions[idx]['Overlap'] = overlap
        idx += 1

    return sessions


def config_summary(config_path):
    f = open(config_path, "r")
    config = json.loads(f.read())
    f.close()

    root_dir = os.path.dirname(config_path)
    no_of_sessions = len(config['Sessions'])

    for s in range(no_of_sessions):
        session = config['Sessions'][s]
        s_id = session['Session']
        s_dir = os.path.join(root_dir, s_id)

        is_reversed = session['ZScan']['Z Increment'] < 0
        print("Imaged from bottom to top" if is_reversed else "Imaged from top to bottom")

        img_res_y = 1e6 * session['YScan']['Pixel Size'] * session['YScan']['Scale Factor']
        img_res_z = 1e6 * session['ZScan']['Z Increment']

        img_res = (abs(img_res_z), 0.23325, img_res_y)
        print(f"Image resolution: {img_res}")

        overlap = round(2048 - abs(1e6 * session['XScan']['X Increment']) / 0.23325)
        print(f"Overlap between strips: {overlap}")
        print(f'\nImaging session: {s}')
        session = config['Sessions'][s]
        s_id = session['Session']
        s_dir = os.path.join(root_dir, s_id)

        lasers = session['Laser Sequence']
        print(f'\tFound laser sequences: {lasers}')

        for l in lasers:
            files = sorted(glob.glob(os.path.join(s_dir, f"*{l}*")))
            pzf_dir = list(filter(os.path.isdir, files))
            print(f'\t{l}: {len(pzf_dir)} Blocks with {len(os.listdir(pzf_dir[0]))} planes')


def get_files(dirctory, z_range=''):
    block = {'h5_filepath': os.path.join(os.path.dirname(dirctory), 'h5', f'{os.path.basename(dirctory)}.h5')}
    zr = z_range_format(z_range)
    block['pzf_files'] = sorted(glob.glob(os.path.join(dirctory, "*.pzf")))[zr]
    return block


def z_range_format(string):
    if string == '':
        return slice(None)
    elif '-' in string:
        return slice(*map(int, string.split('-')))
    else:
        num = int(string)
        return slice(num, num + 1, 1)


def input_format(string):
    if '-' in string:
        return slice(*map(int, string.split('-')))
    else:
        return int(string)


def opt_chunksize(depth, xy_chunks=(256, 256), lower=200, upper=400):
    if depth < lower:
        chunk_d = depth
    else:
        divisor = 1
        chunk_d = depth
        while not (lower <= chunk_d < upper):
            divisor += 1
            chunk_d = math.ceil(depth / divisor)

    return (chunk_d,) + xy_chunks


def session_format(string):
    if string == '':
        return slice(None)
    elif '-' in string:
        return slice(*map(int, string.split('-')))
    else:
        num = int(string)
        return slice(num, num + 1, 1)


def laser_format(string):
    if string == '':
        return 0
    elif ',' in string:
        return string.split(',')
    else:
        return [string]


def pzf_dir_format(string):
    if string == '':
        return slice(None)
    elif '-' in string:
        return slice(*map(int, string.split('-')))
    else:
        num = int(string)
        return slice(num, num + 1, 1)


def get_save_path(project_name="CV"):
    path = pkg_resources.resource_filename("musictune", 'data/save_path.json')
    f = open(path, "r")
    paths = json.loads(f.read())
    f.close()

    return paths[project_name]


def to_zarr(dask_img, prefix, chunk_size=None, save_path=None, dtype=None):
    if chunk_size is None:
        chunk_size = dask_img.chunksize
    if dtype is None:
        dtype = dask_img.dtype

    shape = tuple(map(lambda x, c: (math.ceil(x / c) * c), dask_img.shape, chunk_size))

    store_save = zarr.NestedDirectoryStore(save_path)
    zarr_out = zarr.create(shape, chunks=chunk_size, store=store_save, dtype=dtype, fill_value=0,
                           overwrite=True)

    da.to_zarr(dask_img, zarr_out)
    return save_path


def from_zarr(file_path, chunk_size=None):
    zarr_img = zarr.open(zarr.storage.NestedDirectoryStore(file_path), mode='r')

    if chunk_size is None:
        chunk_size = zarr_img.chunks

    return da.from_zarr(zarr_img, chunks=chunk_size)


def parse_params(param):
    config_path = param['config_path']

    # directories and range options
    s = param['range']['sessions']
    l = param['range']['lasers']
    d = param['range']['pzf_dirs']

    z_range = str(param['range']['z_range'])

    # Line weights and paramters
    line_weights_file = param['lines']['weights_file']
    option = param['lines']['weights_option']
    line_no = param['lines']['single_line_no']

    # Deconvolution parameters
    deconv_status = literal_eval(param['deconvolve']['status'])
    overlap = literal_eval(param['deconvolve']['overlap'])
    psf_path = param['deconvolve']['psf_path']
    psf_res = param['deconvolve']['psf_res']
    iterations = int(param['deconvolve']['iterations'])

    save_path_mod = param['save']['save_path']
    td = param['save']['tmp_dir']

    tmp_chunks = literal_eval(param['save']['tmp_chunks'])
    xy_chunks = literal_eval(param['save']['xy_chunks'])
    zchunk_range = [*map(int, param['save']['zchunk_range'].split('-'))]

    return config_path, s, l, d, z_range, line_weights_file, option, line_no, deconv_status, overlap, psf_path, psf_res, iterations, td, save_path_mod, tmp_chunks, xy_chunks, zchunk_range
