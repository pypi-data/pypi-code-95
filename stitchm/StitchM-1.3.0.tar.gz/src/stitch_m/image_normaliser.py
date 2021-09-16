import numpy as np
import logging


def _image_value_trimmer(image_stack):
    logging.info("Trimming brightest pixels")
    median_std = np.median(np.std(image_stack, axis=(1, 2)))
    new_max = np.median(image_stack) + 2.5 * median_std
    return np.clip(image_stack, 0, new_max)


def exposure_correct(images, exposure_minmax, brightfield_image_list):
    """
    Cockpit saves some exposure min/max data which they use to
    correct exposure when displaying it. This function uses this
    to correct for the exposure.
    """
    logging.info("Applying exposure correction")
    images_min = images[brightfield_image_list].min()
    images_max = images[brightfield_image_list].max()
    images_range = images_max - images_min
    # make broadcastable with brightfield_image_list (propagates to multiplier)
    exp_min = exposure_minmax[brightfield_image_list, 0, np.newaxis, np.newaxis]
    exp_max = exposure_minmax[brightfield_image_list, 1, np.newaxis, np.newaxis]
    multiplier = images_range / (exp_max - exp_min)
    return (images[brightfield_image_list] - exp_min) * multiplier


def normalise_to_datatype(images, datatype, trim=True):
    # Trim images before correction to avoid any speckles
    # leading to the entire image to be quite dark:
    if trim:
        images = _image_value_trimmer(images)
    else:
        images = images.astype(np.float64)  # Convert to float for rescaling

    logging.info("Re-scaling images to %s", datatype)
    
    # Move minimum value of all corrected images to 0:
    np.subtract(images, images.min(), out=images)
    # Convert values to float and rescale so the maximum
    # is set by datatype:
    # New max should be 1 less than the max allowed by datatype
    # so that the background (max) can be made transparent without losing data
    new_max = (np.iinfo(datatype).max - 1)
    multiplier = new_max / images.max()
    np.multiply(images, multiplier, out=images)
    return images


def cast_to_dtype(image, data_type):
    try:
        dtype = np.dtype(data_type)
        if np.issubdtype(dtype, np.integer) and np.issubdtype(image.dtype, np.floating):
            dtype_info = np.iinfo(dtype)
            # Round min/max to avoid this warning when the issue is just going to be rounded away.
            img_min, img_max = round(image.min()), round(image.max())
            min_clip = dtype_info.min > img_min
            max_clip = dtype_info.max < img_max
            if min_clip or max_clip:
                if min_clip:
                    logging.warning(
                        "Image min %f below %s minimum of %i, values below this will be cut off",
                        img_min, dtype, dtype_info.min)
                if max_clip:
                    logging.warning(
                        "Image max %f above %s maximum of %i, values above this will be cut off",
                        img_max, dtype, dtype_info.max)
                np.clip(image, dtype_info.min, dtype_info.max, out=image)
        np.around(image, decimals=0, out=image)
        return image.astype(dtype)
    except Exception:
        logging.error("Invalid data type given: %s aka %s. Saving with default data type.", data_type, dtype)
    return image
