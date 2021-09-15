import os
import zipfile
import logging
import shutil


def zip_folder(path: str, name: str) -> None:
    """
    :param path: path to the existing folder
    :param name: Name of the new zip_folder.zip
    :return: None

    Zip a folder and its content
    """

    def zipdir(new_path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(new_path):
            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(new_path, '../..')))

    zipf = zipfile.ZipFile(f'{name}.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(path, zipf)
    zipf.close()
    logging.info(f'Folder {path} correctly zipped to {os.path.join(os.getcwd(), name)}')
    return None


def unzip_folder(path_to_zip_file: str,
                 directory_to_extract_to: str) -> None:
    """
    :param path_to_zip_file: path to existing zip file
    :param directory_to_extract_to: path to extract-to
    :return: None

    Unzip a folder ant its content
    """
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
    logging.info(f'Folder {path_to_zip_file} correctly unzipped to {directory_to_extract_to}')


def copy_file(original: str,
              target: str) -> None:
    """
    :param original: original path
    :param target: destination path
    :return: None

    Copy a file from original to target
    """
    if os.path.exists(original):
        shutil.copyfile(original, target)
        logging.info(f'Copied file {original} to {target}')
    else:
        logging.error(f"File {original} not found")


def delete_file(path: str) -> None:
    """
    :param path: path of the file to be deleted
    :return: None

    Delete a file
    """
    if os.path.exists(path):
        # removing the file using the os.remove() method
        os.remove(path)
        logging.info(f'{path} correctly deleted')
    else:
        # file not found message
        logging.error(f"File {path} not found")


def delete_folder(path: str) -> None:
    """
    :param path:
    :return: None

    Delete a folder
    """
    try:
        shutil.rmtree(path)
        logging.info(f'Folder {path} deleted')
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))

