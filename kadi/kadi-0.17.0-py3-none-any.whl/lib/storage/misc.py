# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

from flask import current_app
from PIL import Image

from .local import LocalStorage


def create_misc_uploads_path(filename):
    """Create a path from a filename suitable for storing miscellaneous uploads.

    Will use the local path set in ``MISC_UPLOADS_PATH`` in the application's
    configuration as base storage path.

    :param filename: The name of the file.
    """
    filepath = LocalStorage.filepath_from_name(filename, dir_len=2, num_dirs=2)
    return os.path.join(current_app.config["MISC_UPLOADS_PATH"], filepath)


def save_as_thumbnail(image_name, file_object, max_image_size=(512, 512)):
    """Save an image file as JPEG thumbnail.

    Will use the local path set in ``MISC_UPLOADS_PATH`` in the application's
    configuration as base storage path.

    :param image_name: The unique identifier of the thumbnail.
    :param file_object: The image file object.
    :param max_image_size: (optional) The maximum size of the thumbnail.
    :return: ``True`` if the thumbnail was saved successfully, ``False`` otherwise.
    """
    filepath = create_misc_uploads_path(image_name)
    storage = LocalStorage(max_size=current_app.config["MAX_IMAGE_SIZE"])

    try:
        storage.save(filepath, file_object)
        mimetype = storage.get_mimetype(filepath)

        if mimetype in current_app.config["IMAGE_MIMETYPES"]:
            with Image.open(filepath) as image:
                image = image.convert("RGBA")
                image.thumbnail(max_image_size)

                # Convert transparent background into white background.
                bg = Image.new("RGB", image.size, color=(255, 255, 255))
                bg.paste(image, mask=image.split()[-1])
                image = bg

                image.save(filepath, format="JPEG")

            return True

    except Exception as e:
        current_app.logger.exception(e)

    return False


def delete_thumbnail(image_name):
    """Delete a thumbnail.

    This is the inverse operation of :func:`save_as_thumbnail`.

    :param image_name: See :func:`save_as_thumbnail`.
    """
    filepath = create_misc_uploads_path(image_name)
    storage = LocalStorage()

    storage.delete(filepath)
    storage.remove_empty_parent_dirs(filepath, num_dirs=2)
