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
import pathlib
import tarfile
import zipfile
from collections import OrderedDict


def _archive_contents_to_list(contents):
    results = []

    for name, content in contents.items():
        item = {"name": name, **content}

        if content["is_dir"]:
            item["children"] = _archive_contents_to_list(item["children"])

        results.append(item)

    return sorted(results, key=lambda item: (not item["is_dir"], item["name"]))


def get_archive_contents(filename, mimetype, max_entries=100):
    """Get information about the contents contained in an archive.

    :param filename: The filename of the archive.
    :param mimetype: The MIME type of the archive. One of ``"application/zip"``,
        ``"application/gzip"``, ``"application/x-tar"`` or ``"application/x-bzip2"``.
    :param max_entries: (optional) The maximum number of entries to collect information
        from. A ``None`` value will remove this limit.
    :return: An empty list if the contents could not be obtained or a list of archive
        entries in the following form:

        .. code-block:: python3

            [
                {
                    "name": "dogs",
                    "is_dir": True,
                    "children": [],
                },
                {
                    "name": "cat.png",
                    "is_dir": False,
                    "size": 12345,
                },
            ]
    """
    entries = []

    if mimetype == "application/zip":
        try:
            with zipfile.ZipFile(filename) as zip_file:
                entries = zip_file.infolist()

                if max_entries is not None:
                    entries = entries[:max_entries]

        except zipfile.BadZipFile:
            return entries

    elif mimetype in ["application/gzip", "application/x-tar", "application/x-bzip2"]:
        try:
            with tarfile.open(filename) as tar_file:
                num_entries = 0

                for entry in tar_file:
                    entries.append(entry)
                    num_entries += 1

                    if max_entries is not None and num_entries >= max_entries:
                        break

        except tarfile.TarError:
            return entries

    else:
        return entries

    contents = OrderedDict()

    for entry in entries:
        if isinstance(entry, zipfile.ZipInfo):
            is_dir = entry.filename.endswith("/")
            size = entry.file_size

            items = entry.filename.split("/")
            if not is_dir:
                name = items[-1]
                parents = items[:-1]
            else:
                name = items[-2]
                parents = items[:-2]

        elif isinstance(entry, tarfile.TarInfo):
            is_dir = entry.isdir()
            size = entry.size

            items = entry.name.split("/")
            name = items[-1]
            parents = items[:-1]

        current_dir = contents

        for parent in parents:
            if parent not in current_dir:
                # Depending on how the archive was created, not all directories might be
                # listed separately.
                current_dir[parent] = {"is_dir": True, "children": OrderedDict()}

            current_dir = current_dir[parent]["children"]

        # Depending on how the archive was created, some entries might be listed
        # multiple times.
        if name in current_dir:
            continue

        current_dir[name] = {"is_dir": is_dir}
        if not is_dir:
            current_dir[name]["size"] = size
        else:
            current_dir[name]["children"] = OrderedDict()

    return _archive_contents_to_list(contents)


def _rename_duplicate_entry(filename, index):
    path = pathlib.Path(filename)

    base = ""
    if len(path.parts) > 1:
        base = os.path.join(*path.parts[:-1])

    filename = f"{path.stem}_{index}{path.suffix}"
    return os.path.join(base, filename)


def create_archive(filename, entries, callback=None):
    """Create a ZIP archive containing specific files.

    Files with a duplicate name will be renamed to
    ``"<basename> (<index>)<extension>"``. The index starts at 1 and will be incremented
    for each subsequent file having the same name.

    :param filename: The complete name of the new archive.
    :param entries: A list of archive entries to include. Each entry must be a
        dictionary containing the ``path``, the ``name`` (as it should appear in the
        archive) and the ``size`` of the file to include.
    :param callback: (optional) A callback function that will be called after each entry
        that is written to the archive. The function will be called with the current
        number of packaged files and the current size of the archive. The callback has
        to return a boolean indicating whether the packaging process should continue
        (``True``) or not (``False``).
    :return: ``True`` if the archive was created successfully, ``False`` otherwise.
    """
    current_size = 0
    with zipfile.ZipFile(
        filename, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for count, entry in enumerate(entries, 1):
            entry_path = entry["path"]
            entry_name = entry["name"]

            index = 1
            while True:
                try:
                    # Check if a file with that name already exists in the archive. If
                    # yes, try to rename it.
                    archive.getinfo(entry_name)
                    entry_name = _rename_duplicate_entry(entry["name"], index)
                    index += 1
                except KeyError:
                    break

            archive.write(entry_path, arcname=entry_name)
            current_size += entry["size"]

            if callback is not None and not callback(count, current_size):
                return False

    return True
