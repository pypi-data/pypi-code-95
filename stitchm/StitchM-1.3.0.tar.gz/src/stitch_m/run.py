import sys
import logging

from .__init__ import __version__


def sort_args_then_run():
    from .log_handler import LogHandler
    from .file_handler import argument_organiser, get_config, create_user_config, create_Windows_shortcut, boolean_config_handler
    try:
        argv = sys.argv[1:]
        # Allows setup options without StitchM script interface:
        create_usr_config = "-cfg" in argv or "--config" in argv
        create_win_shortcut = "-win" in argv or "--windows-shortcut" in argv
        if create_usr_config or create_win_shortcut:
            with LogHandler("info", "info"):
                if create_usr_config:
                    create_Windows_shortcut()
                if create_win_shortcut:
                    create_user_config()

        config, config_messages = get_config()
        with LogHandler(config=config, config_messages=config_messages):
            logging.info("StitchM given arguments: %s", argv)
            args = argument_organiser(argv)
            logging.info("Sorted arguments: %s", args)
            if args[0] is not None:
                if len(args) > 2:
                    args = args[0:2]
                main_run(config, *args)
                if boolean_config_handler(config, 'OTHER', 'wait upon completion', default=False):
                    input("Processing complete! Press enter to exit")
                return
            else:
                logging.error("No valid mosaic file")
    except IOError:
        logging.error('Error has occurred while stitching or saving mosaic. Please see traceback for more info.', exc_info=True)
    except Exception:
        logging.error("Unknown error occurred. Please see traceback for more info.", exc_info=True)
    if boolean_config_handler(config, 'OTHER', 'wait upon failure', default=True):
        input("Processing failed! Press enter to exit")

def _stitch(config, mosaic, markers, normalise):
    from pathlib import Path
    from .file_handler import is_mosaic_file, is_marker_file, boolean_config_handler
    from .unstitched_image import UnstitchedImage
    from .metadata_maker import MetadataMaker
    from .stitcher import Stitcher
    dtype = "uint16"
    try:
        if is_mosaic_file(mosaic):
            mosaic_path = Path(mosaic).resolve()  # Gets absolute path of mosaic file
            tiff_path = mosaic_path.with_suffix(".ome.tiff")

            unstitched = UnstitchedImage(mosaic_path)
            stitcher = Stitcher(dtype)
            mosaic_array = stitcher.make_mosaic(unstitched, boolean_config_handler(config, 'PROCESSING', 'filter', default=True), normalise)
            metadata_creator = MetadataMaker(tiff_path.name, unstitched, dtype)

            if markers is not None and is_marker_file(markers) and Path(markers).is_file():
                tiff_name = tiff_path.name.replace(".ome.tiff", "_marked.ome.tiff")
                tiff_path = tiff_path.parent / tiff_name
                metadata_creator.add_markers(tiff_name, markers)
            return mosaic_array, metadata_creator.get(), str(tiff_path)
        else:
            logging.error("Mosaic file path cannot be resolved")
            raise IOError("Mosaic file path cannot be resolved")
    except Exception:
        arg_string = ", ".join((str(mosaic or None), str(markers or None), str(normalise)))
        logging.error("Invalid arguments: %s", arg_string, exc_info=True)
        if boolean_config_handler(config, 'OTHER', 'wait upon failure', default=True):
            input("Processing failed! Press enter to exit")
        raise IOError("Invalid arguments: %s", arg_string)
    

def _save(mosaic, metadata, tiff_filename):
    import tifffile as tf
    from numpy import iinfo, uint32
    try:
        logging.info("Saving %s", tiff_filename)
        bigtiff = mosaic.size * mosaic.itemsize >= iinfo(uint32).max  # Check if data bigger than 4GB TIFF limit
        with tf.TiffWriter(tiff_filename, bigtiff=bigtiff, ome=False) as tif:
            tif.write(
                mosaic,
                description=metadata.to_xml().encode(),
                photometric='MINISBLACK',
                metadata={'axes':'YX'},
                software=f"StitchM {__version__}")
    except Exception:
        logging.error("Cannot save: %s", tiff_filename, exc_info=True)
        raise IOError("Cannot save: {}".format(tiff_filename))

def main_run(config, mosaic, markers=None, normalise=True):
    """
    PARAMETERS:
        mosaic - Path of .txt file that contains the mosaic information, including the path to the .mrc file
        markers - Path of .txt file that contains a list of marker placements and associated numbers (please make sure this correctly corresponds to the mosaic file)
        normaliseOff - boolean that specifies if we should not normalise the image. 
    
    The output will be saved as the mosaic filename, with the suffix '.ome.tiff' (or '_marked.ome.tiff' if markers are supplied), in same directory as the mosaic file.
    """
    logging.info("Running StitchM with arguments: mosaic=%s, markers=%s, normalise=%s", mosaic, markers, normalise)
    mosaic, metadata, tiff_file = _stitch(config, mosaic, markers, normalise)
    _save(mosaic, metadata, tiff_file)