import os
import zipfile


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
                                           os.path.join(new_path, '..')))

    zipf = zipfile.ZipFile(f'{name}.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(path, zipf)
    zipf.close()
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
