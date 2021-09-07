import os
import shutil
import time
from os.path import expanduser

from distributed import Client
from musictune.deconvolution.deconvolve import deconvolve_parallel

home = expanduser("~")
os.environ['MPLCONFIGDIR'] = os.path.join(home, '.matplotlib')

import h5py as h5
from musictune.io.modules import *
from musictune.io.utilities import *

scheduler_path = os.path.join(home, 'scheduler.json')

import sys


def main():
    global shape
    print(r"""
         __  __        ____ ___ _____   __                 
        |  \/  | _   _/ ___|_ _/ ___|  / /___  ______  ___ 
        | |\/| || | | \___ \| | |     / __/ / / / __ \/ _ \
        | |  | || |_| |___) | | |___ / /_/ /_/ / / / /  __/
        |_|  |_/| ._,_|____/___\____|\__/\__,_/_/ /_/\___/ 
                |_|                                    """)
    if len(sys.argv[1:]) > 0:
        param_path = sys.argv[1]
    else:
        val = input(
            "You need to enter parameters one by one; alternatively, you can provide a parameters.json file as an argument. Do you wish to continue here? (y/n):")

        if val != 'y':
            sys.exit()

        param = {}
        while True:
            config_path = input("Enter config path (e.g. /home/BlockR.json):")
            if not os.path.isfile(config_path):
                print("Invalid file path.")
                continue
            else:
                config_summary(config_path)
                param['config_path'] = config_path
                break

        param['range'] = {}
        range_mod = input("Do you wish to modify the processing range? (y/n):")
        if range_mod == 'y':
            while True:
                s = input("\tEnter session number or range (e.g. 0 or 0-2) - leave blank to process all:")
                try:
                    session_format(s)
                    param['range']['sessions'] = s
                    break
                except:
                    print("\tInvalid input")

            while True:
                l = input("\tEnter laser/s wavelength (e.g. 561,640) - leave blank to process all:")
                try:
                    laser_format(l)
                    param['range']['lasers'] = l
                    break
                except:
                    print("\tInvalid input")

            while True:
                d = input("\tEnter block range (e.g. 10-15) - leave blank to process all:")
                try:
                    pzf_dir_format(d)
                    param['range']['pzf_dirs'] = d
                    break
                except:
                    print("\tInvalid input")

            while True:
                z_range = input("\tEnter z-depth range (e.g. 100-250) - leave blank to process all:")
                try:
                    z_range_format(z_range)
                    param['range']['z_range'] = z_range
                    break
                except:
                    print("\tInvalid input")
        else:
            param['range']['sessions'] = ""
            param['range']['lasers'] = ""
            param['range']['pzf_dirs'] = ""
            param['range']['z_range'] = ""

        param['lines'] = {}
        line_mod = input("Do you wish to modify line merging options? (y/n):")
        if line_mod == 'y':
            while True:
                line_weights_file = input("\tEnter path to line_weights.json - leave blank to use the default weights:")
                if not (os.path.isfile(line_weights_file) or line_weights_file == ""):
                    print("\tInvalid file path.")
                    continue
                else:
                    param['lines']['weights_file'] = line_weights_file
                    break

            while True:
                option = input("\tChoose a method to combine lines (merge or single):")
                if not option in ["merge", "single"]:
                    print("\tInvalid choice")
                    continue
                else:
                    param['lines']['weights_option'] = option
                    break

            if option == "single":
                while True:
                    line_no = int(input("\tChoose a line number from 0 to 7:"))
                    if not 0 <= line_no <= 7:
                        print("\tInvalid line number")
                        continue
                    else:
                        param['lines']['single_line_no'] = 0
                        break
            else:
                param['lines']['single_line_no'] = 0
        else:
            param['lines']['weights_file'] = ""
            param['lines']['weights_option'] = "merge"
            param['lines']['single_line_no'] = 0

        param['deconvolve'] = {}
        ds = input("Do you wish to deconvolve the blocks (y/n):")
        if ds == 'y':
            param['deconvolve']['status'] = "True"
            while True:
                overlap = input("\tEnter overlaps between chunks (e.g. (64,32,32)):")
                try:
                    literal_eval(overlap)
                    param['deconvolve']['overlap'] = overlap
                    break
                except:
                    print("\tInvalid overlap value")

            while True:
                psf_path = input("\tEnter PSF file path or enter 'measured' or 'theoretical':")
                if psf_path in ['measured', 'theoretical']:
                    param['deconvolve']['psf_path'] = psf_path
                    break
                elif not os.path.isfile(psf_path):
                    print("\tInvalid PSF file path")
                    continue
                else:
                    param['deconvolve']['psf_path'] = psf_path
                    break

            if not psf_path in ['measured', 'theoretical']:
                while True:
                    psf_res = input("\tEnter PSF resolution in \mum (e.g. (0.9,0.9,0.9)):")
                    try:
                        literal_eval(psf_res)
                        param['deconvolve']['psf_res'] = psf_res
                        break
                    except:
                        print("Invalid resolution value")
            else:
                param['deconvolve']['psf_res'] = ""

                while True:
                    iterations = input("\tEnter deconvolution iterations (preferred: 10-50):")
                    try:
                        int(iterations)
                        param['deconvolve']['iterations'] = iterations
                        break
                    except:
                        print("\tInvalid iterations value")
        else:
            param['deconvolve']['status'] = "False"
            param['deconvolve']['overlap'] = "(0,0,0)"
            param['deconvolve']['psf_path'] = ""
            param['deconvolve']['psf_res'] = ""
            param['deconvolve']['iterations'] = "0"

        param['save'] = {}
        while True:
            save_path_mod = input("Enter save directory:")
            if not (os.path.isdir(save_path_mod) or save_path_mod == ""):
                print("Invalid directory")
            else:
                param['save']['save_path'] = save_path_mod
                break

        param['save']['tmp_dir'] = 'TMP'
        param['save']['tmp_chunks'] = "(1,512,512)"
        param['save']['xy_chunks'] = "(256,256)"
        param['save']['zchunk_range'] = "200-300"

        param_path = os.path.join(home, 'param_pzf2zarr.json')

        with open(param_path, 'w') as outfile:
            json.dump(param, outfile, indent=4)

        print(f"File saved successfully at {param_path}")
    f = open(param_path, "r")
    param = json.loads(f.read())
    f.close()
    config_path, s, l, d, z_range, line_weights_file, option, line_no, deconv_status, overlap, psf_path, psf_res, iterations, td, save_path_mod, tmp_chunks, xy_chunks, zchunk_range = parse_params(
        param)
    f = open(config_path, "r")
    config = json.loads(f.read())
    f.close()
    sessions, total_blocks = read_config(config_path, s, l, d)
    tmp_dir = os.environ.get(td)
    if not tmp_dir:
        tmp_dir = td
    if line_weights_file == "":
        f = open(pkg_resources.resource_filename("musictune", 'data/Weights.json'), "r")
        weights = json.loads(f.read())
        f.close()
    else:
        f = open(line_weights_file, "r")
        weights = json.loads(f.read())
        f.close()
    if psf_path == "measured":
        psf_path = pkg_resources.resource_filename("musictune", 'data/PSF/CV_us_640_fine.tif')
        psf_res = (0.23325, 0.23325, 0.23325)
    elif psf_path == "theoretical":
        psf_path = pkg_resources.resource_filename("musictune", 'data/PSF/PSF_16bit_full.tif')
        psf_res = (0.933, 0.933, 0.933)

    client = Client(scheduler_file=scheduler_path)

    start_time = time.time()
    start_index = weights['ReadCrop']['index']
    crop_length = weights['ReadCrop']['length']
    weight = np.array(weights['Weight'])
    weighted_pixels = np.expand_dims(weight, 1) * np.array(weights['Weighted Pixels'])

    if save_path_mod == "":
        project_path = get_save_path(config['Basename']["Project"])
    else:
        project_path = save_path_mod
    save_root = os.path.join(project_path, config['Basename']["Sample"])
    save_dir = os.path.join(save_root, config['Basename']["Sequence"])

    elapsed_block_time = 0
    processed_blocks = 0

    block_time = time.time()
    for sess in sessions:
        print(f"Processing session: {sess}")
        img_res = sessions[sess]['Image Resolution']
        print(f"Image resolution: {img_res}")
        psf_invert = not sessions[sess]['Reversed']

        lasers = sessions[sess]['Files']
        grid = 1e8 * np.arange(sessions[sess]['Image Start'], sessions[sess]['Image End'],
                               sessions[sess]['Pixel Size'] * sessions[sess]['Scale Factor'])

        for las in lasers:
            print(f"\tProcessing Lasers: {las}")
            directories = lasers[las]

            for pzf_dir in directories:
                try:
                    eta = round((total_blocks - processed_blocks) * (elapsed_block_time / processed_blocks))
                except:
                    eta = 'N/A'

                print(f"\n\n\t\tNumber of blocks processed: {processed_blocks}/{total_blocks}")
                print(f"\t\tEstimated time remaining (seconds): {eta}")

                print(f"\n\n\t\tProcessing Block: {pzf_dir}")

                block = get_files(pzf_dir, z_range=z_range)

                sample = decompress(block['pzf_files'][0]).compute()

                delayed_planes = [decompress(fn) for fn in block['pzf_files']]
                delayed_planes = [da.from_delayed(x, shape=sample.shape, dtype='f4') for x in delayed_planes]

                da_line_planes = da.stack(delayed_planes)

                coordinate_file = h5.File(block['h5_filepath'], 'r')
                coordinates = da.from_array(
                    np.expand_dims(
                        np.array([coordinate_file.get(fn.split(os.sep)[-1])[:] for fn in block['pzf_files']]),
                        1), chunks=(1, 1, da_line_planes.chunksize[-1]))

                ## Merge lines
                merge_chunk_size = (1, da_line_planes.chunksize[1], 1, da_line_planes.chunksize[3])

                da_planes = da.map_blocks(merge_lines, da_line_planes, weighted_pixels, option=option,
                                          start_index=start_index,
                                          crop_length=crop_length, line_no=line_no, chunks=merge_chunk_size,
                                          dtype='f4').squeeze()

                da_planes_repositioned = da.map_blocks(reposition_lines, da_planes, coordinates, grid, dtype='f4')

                save_path = os.path.join(save_dir, *pzf_dir.split(os.sep)[-2:]) + '.zarr'
                tmp_save_path = tmp_dir + save_path

                shape = tuple(map(lambda x, c: (math.ceil(x / c) * c), da_planes.shape, tmp_chunks))

                store = zarr.NestedDirectoryStore(tmp_save_path)
                z_out = zarr.create(shape=shape, chunks=tmp_chunks, dtype=da_planes.dtype, store=store, overwrite=True,
                                    fill_value=0)

                print(f"\t\tSaving tmp image: {tmp_save_path}")
                da.to_zarr(da_planes_repositioned, z_out)

                chunk_size = opt_chunksize(da_planes.shape[0], xy_chunks, zchunk_range[0], zchunk_range[1])

                dask_img = from_zarr(tmp_save_path, chunk_size=chunk_size)
                print(f"\t\tRechunking image: {dask_img}")

                if deconv_status:
                    print("\t\tDeconvolving")

                    dask_img = deconvolve_parallel(dask_img,
                                                   img_resolution=img_res,
                                                   chunk_size=chunk_size,
                                                   overlap=overlap,
                                                   psf_invert=psf_invert,
                                                   psf_path=psf_path,
                                                   psf_res=psf_res,
                                                   iterations=iterations)

                path = to_zarr(dask_img, prefix='', chunk_size=chunk_size, save_path=save_path)

                print(f"\t\tSaved:{path}")

                shutil.rmtree(tmp_save_path)
                print("\t\tTmp file removed\n")
                elapsed_block_time = time.time() - block_time
                processed_blocks += 1
    elapsed_time = time.time() - start_time
    print("Elapsed total time: ", elapsed_time)
    config["ZARR Conversion"] = param
    config["ZARR Conversion"]["elapsed_time"] = elapsed_time
    with open(os.path.join(save_root, config['Basename']['Sequence'] + '.json'), 'w') as outfile:
        json.dump(config, outfile, indent=4)
    client.close()


if __name__ == "__main__":
    main()
