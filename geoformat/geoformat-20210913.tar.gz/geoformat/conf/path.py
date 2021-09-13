from pathlib import Path

from geoformat.conf.error_messages import path_not_valid, path_not_valid_file_exists_overwrite_is_false


def add_extension_path(path, add_extension):
    """
    Add extension to path if add extension is specified

    :param path: input path
    :param add_extension:
    :return: output path
    """
    if add_extension and add_extension != path.suffix:
        path = path.with_suffix(path.suffix + add_extension)

    return path


def verify_input_path_is_file(path):
    """
    Transform str path to Path object from pathlib if given path exists and is a file
    :param path: str path or pathlib Path object
    :return: Path object
    """
    p = Path(path)
    if p.is_file():
        return p
    else:
        raise Exception(path_not_valid.format(path=path))


def path_to_file_path(path, geolayer_name, overwrite=True, add_extension=None):
    """
    Return verified file path for input path.
    Make difference between path dir and path file and return always

    :param path: dir path or file path to be checked.
    :param geolayer_name: name of geolayer (only used when path is dir path)
    :param overwrite: True we overwrite file if exists, False we return an error if file exists
    :param add_extension: if input path if file (without extension) or dir if add extension is True we add file
    extension specified ('geojson', 'shp', 'kml' ...)
    :return: output path
    """
    p = Path(path)
    file_path = None
    if p.exists() is True:
        # check if is dir
        if p.is_dir() is True:
            file_path = p.joinpath(geolayer_name)
        # chek if it's file
        elif p.is_file():
            file_path = p
    # file or dir does not exists
    else:
        if p.parent.exists():
            file_path = p
        else:
            raise Exception(path_not_valid.format(path=path))

    # add extension
    file_path = add_extension_path(path=file_path, add_extension=add_extension)

    # check overwrite
    if file_path.exists() and overwrite is False:
        raise Exception(path_not_valid_file_exists_overwrite_is_false.format(path=file_path))

    return file_path
