version_info = (1, 3, 0)
__version__ = '.'.join(str(c) for c in version_info)
__author__ = "Thomas Fish"

def stitch_and_save(mosaic_file, marker_file=None):
    """
    PARAMETERS:
        mosaic_file - Path of .txt file that contains the mosaic information, including the path to the .mrc file
        marker_file - Path of .txt file that contains a list of marker placements and associated numbers (please make sure this correctly corresponds to the mosaic file)
    
    The output will be saved as the mosaic filename, with the suffix '.ome.tiff' (or '_marked.ome.tiff' if markers are supplied), in same directory as the mosaic file.
    """
    from .run import main_run
    from .file_handler import get_config

    config, _ = get_config()
    main_run(config, mosaic_file, marker_file)


def stitch(mosaic_file, marker_file=None):
    """
    PARAMETERS:
        mosaic_file - Path of .txt file that contains the mosaic information, including the path to the .mrc file
        marker_file - Path of .txt file that contains a list of marker placements and associated numbers (please make sure this correctly corresponds to the mosaic file)
    
    OUTPUT:
        mosaic (numpy array)
        metadata (as an editable omexml object)
        tiff_file (the default path stitch_and_save would save to, as a string)
    """
    from .run import _stitch
    from .file_handler import get_config
    
    config, _ = get_config()
    return _stitch(config, mosaic_file, marker_file)


def save(mosaic, metadata, tiff_file):
    """
    PARAMETERS:
        mosaic - numpy array
        metadata - omexml object from the stitch function (or omexml-dls)
        tiff_file - Path which the mosaic should be saved to (as a string)
    
    The output will be saved as the mosaic filename, with the suffix '.ome.tiff' (or '_marked.ome.tiff' if markers are supplied), in same directory as the mosaic file.
    """
    from .run import _save

    _save(mosaic, metadata, tiff_file)
