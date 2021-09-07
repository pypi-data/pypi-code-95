#!/usr/bin/env python
import os
import posixpath
import hashlib
from flask import current_app
import logging
import fk

logger = logging.getLogger(__name__)


# from https://github.com/pallets/flask/blob/024f0d384cf5bb65c76ac59f8ddce464b2dc2ca1/src/flask/helpers.py

# what separators does this operating system provide that are not a slash?
# this is used by the send_from_directory function to ensure that nobody is
# able to access files from outside the filesystem.
_os_alt_seps = list(sep for sep in [os.path.sep, os.path.altsep] if sep not in (None, "/"))


def safe_join(directory, *pathnames):
    """Safely join `directory` and zero or more untrusted `pathnames`
    components.
    Example usage::
        @app.route('/wiki/<path:filename>')
        def wiki_page(filename):
            filename = safe_join(app.config['WIKI_FOLDER'], filename)
            with open(filename, 'rb') as fd:
                content = fd.read()  # Read and process the file content...
    :param directory: the trusted base directory.
    :param pathnames: the untrusted pathnames relative to that directory.
    :raises: :class:`~werkzeug.exceptions.NotFound` if one or more passed
            paths fall out of its boundaries.
    """

    parts = [directory]

    for fn in pathnames:
        if fn != "":
            pre = fn
            fn = posixpath.normpath(fn)
            # logger.info(f"fn={fn}, pre={pre}")
        if any(sep in fn for sep in _os_alt_seps) or os.path.isabs(fn) or fn == ".." or fn.startswith("../"):
            # logger.info(f"pathname was invalid: {fn}")
            return None

        parts.append(fn)

    return posixpath.join(*parts)


expiry_cache = {}


def get_expiry(path_raw):
    direc = current_app.config["static-files-root"]
    static_prefix = "/static/"
    path = path_raw[len(static_prefix) :] if path_raw.startswith(static_prefix) else path_raw
    filename_temp = os.fspath(path)
    directory = os.fspath(direc)
    filename = safe_join(directory, filename_temp)
    # logger.info(f"path={path}, direc={direc}, filename_temp={filename_temp}, directory={directory}, filename={filename}")
    if not filename:
        # logger.info("No filename returned from safejoin")
        return path_raw
    if not os.path.isabs(filename):
        # logger.info(f"{filename} was not abolute")
        filename = os.path.join(current_app.root_path, filename)
    try:
        if os.path.isfile(filename):
            if not filename in expiry_cache:
                m = hashlib.sha256(fk.utils.read_file(filename).encode("utf-8"))
                expiry_cache[filename] = m.hexdigest()[0:6]
            return f"{path_raw}?expiry_hash={expiry_cache[filename]}"
        else:
            # logger.info(f"filename={filename} was not afile")
            pass
    except Exception as e:
        # logger.info(f"Exception:{e}", exc_info=True)
        pass
    return path_raw
