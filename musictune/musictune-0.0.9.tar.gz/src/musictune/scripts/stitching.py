import os
import time
from os.path import expanduser

import numpy as np
from distributed import Client
from numpy import genfromtxt

home = expanduser("~")
os.environ['MPLCONFIGDIR'] = os.path.join(home, '.matplotlib')

from musictune.io.utilities import *

scheduler_path = os.path.join(home, 'scheduler.json')

import sys


def combine(img1, img2, overlap):
    upper = img1[:, :-overlap, :]
    lower = img2[:, overlap:, :]
    mid_overlap = img1[:, -overlap:, :] + img2[:, :overlap, :]
    return da.concatenate([upper, mid_overlap, lower], axis=1)


def sum_lines(img, scale_factor):
    line = img[:, 0::scale_factor, :]

    for i in range(1, scale_factor):
        line += img[:, i::scale_factor, :]

    return line


def create_line_weights(overlap, cutoff, adjustment):
    lw_start, lw_mid, lw_end = np.ones((2048,)), np.ones((2048,)), np.ones((2048,))
    lw_start[-cutoff:] = 0
    lw_start[-overlap + cutoff:-cutoff] = np.linspace(1, 0, overlap - 2 * cutoff)
    lw_start *= adjustment
    lw_mid[:cutoff] = 0
    lw_mid[-cutoff:] = 0
    lw_mid[cutoff:overlap - cutoff] = np.linspace(0, 1, overlap - 2 * cutoff)
    lw_mid[-overlap + cutoff:-cutoff] = np.linspace(1, 0, overlap - 2 * cutoff)
    lw_mid *= adjustment
    lw_end[:cutoff] = 0
    lw_end[cutoff:overlap - cutoff] = np.linspace(0, 1, overlap - 2 * cutoff)
    lw_end *= adjustment

    return lw_start, lw_mid, lw_end


def find_line_profile(files):
    m_all = []
    for f in files:
        m = np.mean(from_zarr(f), axis=(0, 2)).compute()
        m_all.append(m)

    m_median = np.median(np.array(m_all), axis=0)
    mean_line_norm = (m_median + 1e-10) / (np.max(m_median))
    return np.minimum(1 / mean_line_norm, 100)


def main():
    print(r"""
         __  __        ____ ___ _____   __                 
        |  \/  | _   _/ ___|_ _/ ___|  / /___  ______  ___ 
        | |\/| || | | \___ \| | |     / __/ / / / __ \/ _ \
        | |  | || |_| |___) | | |___ / /_/ /_/ / / / /  __/
        |_|  |_/| ._,_|____/___\____|\__/\__,_/_/ /_/\___/ 
                |_|                                    """)
    if len(sys.argv[1:]) > 0:
        param_path = sys.argv[1]
        f = open(param_path, "r")
        param = json.loads(f.read())
        f.close()
        config_path = param['config_path']
        project, sample, stitch_groups = stitching_summary(config_path)
    else:
        val = input(
            "You need to enter parameters one by one; alternatively, you can provide a parameters.json file as an argument. Do you wish to continue here? ([y]/n):")

        if val == 'n':
            sys.exit()

        param = {}
        while True:
            config_path = input("Enter config path (e.g. /home/BlockR.json):")
            if not os.path.isfile(config_path):
                print("Invalid file path.")
                continue
            else:
                project, sample, stitch_groups = stitching_summary(config_path)
                param['config_path'] = config_path
                break

        print(f"Stitch groups found = {len(stitch_groups)} ")
        for g in stitch_groups:
            print(
                f"Group {g}: {stitch_groups[g]['files'][0]} to {os.path.basename(stitch_groups[g]['files'][-1])} ({len(stitch_groups[g]['files'])} blocks)")

        param['range'] = {}

        while True:
            s = input("\tEnter stitch group number ([all]): ")
            if s == "":
                param['range']['stitch_groups'] = s
            else:
                try:
                    int(s)
                    param['range']['stitch_groups'] = s
                    break
                except:
                    print("\tInvalid input")

        default_path = pkg_resources.resource_filename("musictune", 'data/line_profile.csv')
        param['line_profile'] = {}
        line_mod = input("Modify line profile options? (y/[n]):")
        if line_mod == 'y':
            while True:
                line_weights_file = input("\tLine profile option (profile_path | 'measure' | [default_profile]): ")
                if line_weights_file == "":
                    param['line_profile']['file_path'] = default_path
                    break
                elif line_weights_file == 'measure':
                    param['line_profile']['file_path'] = 'measure'
                    break
                elif not os.path.isfile(line_weights_file):
                    print("\tInvalid file path.")
                    continue
                else:
                    param['line_profile']['file_path'] = line_weights_file
                    break

            while True:
                option = input("\tCutoff value while merging (0-128 | [92]): ")
                if option == "":
                    param['line_profile']['cutoff'] = 92
                    break
                elif not 0 <= int(option) <= 128:
                    print("\tInvalid choice")
                    continue
                else:
                    param['line_profile']['cutoff'] = option
                    break
        else:
            param['line_profile']['file_path'] = default_path
            param['line_profile']['cutoff'] = 92

        param['save'] = {}
        # param['save']['tmp_dir'] = 'TMP'
        # param['save']['tmp_chunks'] = "(1,512,512)"
        param['save']['save_dtype'] = "f4"

        param_path = f'{project}-{sample}-stitching.json'

        with open(param_path, 'w') as outfile:
            json.dump(param, outfile, indent=4)

        print(f"File saved successfully at {param_path}")

    f = open(param_path, "r")
    param = json.loads(f.read())
    f.close()

    config_path = param['config_path']
    f = open(config_path, "r")
    config = json.loads(f.read())
    f.close()

    line_file_path = param['line_profile']['file_path']

    sg = param['range']['stitch_groups']
    if sg != "":
        stitch_groups = {sg: stitch_groups[int(sg)]}

    print(f"Length of groups: {len(stitch_groups)}")

    if line_file_path != 'measure':
        line_profile = genfromtxt(line_file_path, delimiter=',')
        adjustment = np.minimum(1 / line_profile, 5)
    cutoff = int(param['line_profile']['cutoff'])

    save_dtype = param['save']['save_dtype']

    print("Attempting to connect to a cluster..")
    client = Client(scheduler_file=scheduler_path)

    start_time = time.time()

    for s in stitch_groups:
        print(f'Stitch group: {s}')

        files = stitch_groups[s]['files']
        overlap = stitch_groups[s]['overlap']
        img_resolution = stitch_groups[s]['img_resolution']
        print(stitch_groups[s])

        if line_file_path == 'measure':
            adjustment = find_line_profile(files)

        lw_start, lw_mid, lw_end = create_line_weights(overlap, cutoff, adjustment)
        for f in files:
            if f == files[0]:
                stitched = from_zarr(f) * np.expand_dims(lw_start, axis=(0, -1))
            elif f == files[-1]:
                tmp = from_zarr(f) * np.expand_dims(lw_end, axis=(0, -1))
                stitched = combine(stitched, tmp, overlap)
            else:
                tmp = from_zarr(f) * np.expand_dims(lw_mid, axis=(0, -1))
                stitched = combine(stitched, tmp, overlap)

        chunk_size = stitched.chunksize
        scale_factor = int(img_resolution[2] / img_resolution[1])
        stitched_chunks = (chunk_size[0], round(chunk_size[1] / scale_factor), chunk_size[2])

        stitched_iso = da.map_blocks(sum_lines, stitched, scale_factor, chunks=stitched_chunks, dtype=save_dtype)

        dir_name = os.path.dirname(files[0])
        start_block = os.path.basename(files[0])[:-5]
        end_block = os.path.basename(files[-1]).split('_')[-1]
        save_path = f'{dir_name}_{start_block}_to_{end_block}'
        print(save_path)

        shape = tuple(map(lambda x, c: (math.ceil(x / c) * c), stitched_iso.shape, chunk_size))

        store_save = zarr.NestedDirectoryStore(save_path)
        zarr_out = zarr.create(shape, chunks=chunk_size, store=store_save, dtype=save_dtype, fill_value=0,
                               overwrite=True)
        da.to_zarr(stitched_iso, zarr_out)

    elapsed_time = time.time() - start_time
    print("Elapsed time:", elapsed_time)

    config["Stitching"] = param
    config["Stitching"]["elapsed_time"] = elapsed_time

    base_name = config['Basename']
    zarr_conversion = config['ZARR Conversion']
    project_path = zarr_conversion['save']['save_path']
    save_root = os.path.join(project_path, base_name['Sample'], base_name['Sequence'])

    with open(save_root + '_stitched.json', 'w') as outfile:
        json.dump(config, outfile, indent=4)
    client.close()


if __name__ == "__main__":
    main()
