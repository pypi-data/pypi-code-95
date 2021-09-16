import numpy as np
import logging
from numpy.testing import assert_array_equal

from .edge_definer import image_edge_definer
from .image_normaliser import normalise_to_datatype, cast_to_dtype


class Stitcher():

    def __init__(self, datatype="uint16"):
        '''Default datatype="uint16"'''
        self.dtype = np.dtype(datatype)
        self.brightfield_list = []

    def make_mosaic(self, unstitched, fl_filter=True, normalise=True):
        logging.info("Creating mosaic")
        if unstitched.img_count == unstitched.images.shape[0]:
            if fl_filter:
                self.brightfield_list = self._find_brightfield_images(unstitched.img_count, unstitched.exposure_minmax)
            else:
                self.brightfield_list = [i for i in range(unstitched.img_count)]
            # create new large array and load data into it from mosaic:
            mosaic_size = (unstitched.boundaries[1, 0] - unstitched.boundaries[0, 0],
                         unstitched.boundaries[1, 1] - unstitched.boundaries[0, 1])
            
            # If we are not normalising, fill with zero values rather than max
            fill_value = np.iinfo(self.dtype).max * normalise
            mosaic_array = np.full(mosaic_size, fill_value, dtype=self.dtype)
            
            images = unstitched.images[self.brightfield_list]  # Filter out unwanted images
            unstitched.clear_image_array()
            if normalise:
                # Rescale max/min to fit data type
                images = normalise_to_datatype(images, self.dtype, trim=True)
            
            # Cast to output data type
            images = cast_to_dtype(images, self.dtype)

            for i in range(len(self.brightfield_list)):
                start, end = image_edge_definer(
                    unstitched.pix_positionlist[self.brightfield_list[i], :],
                    unstitched.boundaries,
                    unstitched.pix2edge
                    )
                # Array needs to be transposed for python versus dv.
                # This rotates each image so they line up correctly
                mosaic_array[start[0]:end[0], start[1]:end[1]] = images[i, :, :].T
            del(images)
            # Rotate back and flip
            return np.flip(mosaic_array.T, 0)
        else:
            logging.error("Number of images doesn't match between files")
            raise AssertionError("Number of images doesn't match between files")

    def get_brightfield_list(self):
        return self.brightfield_list

    @staticmethod
    def _find_brightfield_images(img_count, minmax):
        """
        This returns a list of indices of "good" images (i.e. not fluorescent 
        images).
        This is based on the min/max values of fluorescent images being 
        lower than the median - 0.5 * std deviation of the min/max of all the  
        images.

        This method is not valid if there are too many fl images to bf images,
        as this will affect the median value, leading to few, if any, images 
        being filtered.

        If more than half of the images are filtered out by this metric,
        it is assumed something hasn't worked correctly and a list including
        of all image indices will be returned.
        """
        full_list = range(0, img_count)

        median_min = np.median(minmax[:, 0])
        std_min = np.std(minmax[:, 0])

        median_max = np.median(minmax[:, 1])
        std_max = np.std(minmax[:, 1])

        good_list = np.nonzero(np.logical_and(
            minmax[:, 1] > median_max - 0.5 * std_max,
            minmax[:, 0] > median_min - 0.5 * std_min))[0].tolist()

        if len(good_list) == img_count:
            logging.info("No potential fluorescence images found.")
        else:
            logging.info(
                "Potential fluorescence images found: '%s' (counted from 0)",
                ", ".join(map(str, np.setdiff1d(full_list, good_list)))
                 )
        if len(good_list) > img_count / 2:
            return good_list
        return full_list
