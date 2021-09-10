import os
import sys
import time
from os.path import expanduser

import SimpleITK as sitk
import dask.array as da
import numpy as np
from distributed import Client
from musictune.io.utilities import from_zarr

home = expanduser("~")
scheduler_path = os.path.join(home, 'scheduler.json')


def save_slice(img, index, filename):
    itkimage = sitk.Cast(sitk.GetImageFromArray(img), sitk.sitkFloat32)
    itkimage.SetSpacing((1.0, 1.0, 1.0))
    sitk.WriteImage(itkimage, os.path.join(filename, 'slice' + str(np.squeeze(index)).zfill(4) + '.tif'), True)
    return np.atleast_3d(1)


def main():
    if len(sys.argv[1:]) > 0:
        file_path = sys.argv[1]
    else:
        file_path = input("Provide a .zarr file path:")

    start_time = time.time()
    da_img = from_zarr(file_path)
    chunk_size = (1, da_img.shape[1], da_img.shape[2])
    da_img = da_img.rechunk(chunk_size)

    index = np.arange(0, da_img.shape[0])
    index = np.expand_dims(index, [1, 2])
    da_index = da.from_array(index, chunks=(1, 1, 1))

    filename, ext = os.path.splitext(file_path)
    basename = os.path.splitext(os.path.basename(file_path))[0]

    filename = filename + '_planes'

    if not os.path.exists(filename):
        os.makedirs(filename)

    client = Client(scheduler_file=scheduler_path)

    da_out = da.map_blocks(save_slice, da_img, da_index, filename, chunks=(1, 1, 1), dtype='uint8')
    da_out.compute()

    print(f"Conversion completed. Elapsed time: {time.time() - start_time}")
    client.close()


if __name__ == "__main__":
    main()
