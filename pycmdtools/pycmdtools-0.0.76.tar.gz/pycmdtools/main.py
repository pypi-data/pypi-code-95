"""
The default group of operations that pycmdtools has
"""
import collections
import json
import os
import shutil
from collections import defaultdict

import pylogconf.core
import yaml
import jsonschema
from pytconf import register_endpoint, get_free_args, register_main, config_arg_parse_and_launch
from tqdm import tqdm
from lxml import etree

from pycmdtools.configs import ConfigFolder, ConfigUseStandardExceptions, ConfigChangeLine, ConfigProgress, \
    ConfigAlgorithm, ConfigDownloadGoogleDrive, ConfigCopy, ConfigDownloadGdriveURL
from pycmdtools.static import DESCRIPTION, APP_NAME, VERSION_STR
from pycmdtools.utils import yield_bad_symlinks, diamond_lines, checksum, download_file_from_google_drive, error, \
    remove_bad_symlinks, gdrive_download_link


@register_endpoint(
    description="Find all bad symbolic links in a folder",
    configs=[
        ConfigFolder,
        ConfigUseStandardExceptions
    ],
)
def find_bad_symlinks() -> None:
    for full in yield_bad_symlinks(
        folder=ConfigFolder.folder,
        use_standard_exceptions=ConfigUseStandardExceptions.use_standard_exceptions,
        onerror=error,
    ):
        print(full)


@register_endpoint(
    description="remove all bad symlinks",
    configs=[
        ConfigFolder,
        ConfigUseStandardExceptions
    ],
)
def symlinks_remove_bad() -> None:
    remove_bad_symlinks(
        folder=ConfigFolder.folder,
        use_standard_exceptions=ConfigUseStandardExceptions.use_standard_exceptions,
    )


@register_endpoint(
    description="Change the first line in files",
    configs=[
        ConfigChangeLine,
    ],
    allow_free_args=True,
)
def change_first_line() -> None:
    changed = 0
    actually_changed = 0
    print(f"from_line is [{ConfigChangeLine.from_line}]")
    print(f"to_line is [{ConfigChangeLine.to_line}]")
    for filename in get_free_args():
        print(f"considering [{filename}]...")
        with open(filename, "rt") as input_handle:
            data = input_handle.readlines()
        if len(data) == 0:
            continue
        # change the first line
        if ConfigChangeLine.from_line is None or data[0] == ConfigChangeLine.from_line + "\n":
            if data[0] != ConfigChangeLine.to_line + "\n":
                actually_changed += 1
            data[0] = ConfigChangeLine.to_line + "\n"
            changed += 1
        with open(filename, "wt") as output_handle:
            output_handle.write("".join(data))
    # print statistics
    print(f"changed is [{changed}]")
    print(f"actually_changed is [{actually_changed}]")


@register_endpoint(
    description="Print unique values and their count",
    allow_free_args=True
)
def line_value_histogram() -> None:
    saw = defaultdict(int)
    for line in diamond_lines(get_free_args()):
        line = line.rstrip()
        saw[line] += 1
    for k, v in saw.items():
        print(f"{k}\t{str(v)}")


@register_endpoint(
    description="Filter out non unique values from a stream, even if not sorted",
    allow_free_args=True
)
def unique() -> None:
    saw = set()
    for line in diamond_lines(get_free_args()):
        if line not in saw:
            saw.add(line)
            print(line, end='')


@register_endpoint(
    description="print all command line arguments",
    allow_free_args=True
)
def print_all_args() -> None:
    print(f"number of command line arguments is {len(get_free_args())}")
    for i, s in enumerate(get_free_args()):
        print(f"{i}: {s}")


@register_endpoint(
    description="follow the progress of another process",
)
def progress() -> None:
    """
    enable to show progress by pointing to a FILE and not a PROCESS NAME or PID.
    If you point to a file then something like fuser(1) should be called
    on the file, and if there is just one process holding the file open
    then show the progress on that file.

    References:
    - https://unix.stackexchange.com/questions/66795/how-to-check-progress-of-running-cp
    - https://github.com/Xfennec/progress
    - https://gist.github.com/azat/2830255
    - https://stackoverflow.com/questions/10980689/how-to-follow-the-progress-of-a-linux-command
    """


@register_endpoint(
    description="Print statistics about a list of numbers",
    allow_free_args=True
)
def stats() -> None:
    total_sum = 0.0
    total_sum2 = 0.0
    count = 0
    for line in diamond_lines(get_free_args()):
        count += 1
        value = float(line)
        total_sum += value
        total_sum2 += value * value
    if count != 0:
        print(total_sum / count)
    else:
        print("no data given")


@register_endpoint(
    description="Validate json files",
    allow_free_args=True,
)
def validate_json() -> None:
    for filename in get_free_args():
        with open(filename, "rt") as input_handle:
            json.load(input_handle)


@register_endpoint(
    description="Validate YAML files",
    allow_free_args=True,
    min_free_args=1,
)
def validate_yaml() -> None:
    for filename in get_free_args():
        with open(filename, "rt") as input_handle:
            yaml.load(input_handle, yaml.SafeLoader)


@register_endpoint(
    description="Validate jsonschame files",
    allow_free_args=True,
    min_free_args=1,
)
def validate_jsonschema() -> None:
    for filename in get_free_args():
        with open(filename, "rt") as stream:
            data = json.load(stream)
            validator = jsonschema.validators.validator_for(data)
            validator.check_schema(data)


@register_endpoint(
    description="Validate XML files",
    allow_free_args=True
)
def validate_xml() -> None:
    for filename in get_free_args():
        etree.parse(filename)


@register_endpoint(
    description="Pick an x profile with some interface from ~/.xprofilerc",
)
def xprofile_select() -> None:
    print("TBD")


@register_endpoint(
    description="compare many files and print identical ones",
    configs=[
        ConfigProgress,
        ConfigAlgorithm,
        ConfigCopy,
    ],
    allow_free_args=True,
    min_free_args=2,
)
def mcmp() -> None:
    """
    TODO:
    - make the algorithm faster by looking only at the beginning of the files.
    - make the algorithm faster by looking at the length of the files.
    - make the algorithm faster by having a gnu dbm ~/.mcmp which already stores
    hashes of known files.
    """
    d = collections.defaultdict(set)
    files = get_free_args()
    if ConfigProgress.progress:
        files = tqdm(files)
    for file_name in files:
        check_sum = checksum(file_name=file_name, algorithm=ConfigAlgorithm.algorithm)
        d[check_sum].add(file_name)
    for i, check_sum in enumerate(sorted(d.keys())):
        print(f"{i}: {', '.join(sorted(d[check_sum]))}")
    if ConfigCopy.copy:
        sorted_keys = sorted(d.keys())
        index_from = int(input("From what version? "))
        index_to = int(input("To what version? "))
        checksum_from = sorted_keys[index_from]
        checksum_to = sorted_keys[index_to]
        set_from = d[checksum_from]
        set_to = d[checksum_to]
        source_file = set_from.pop()
        for target_file in set_to:
            shutil.copy(source_file, target_file)


@register_endpoint(
    description="Download a file from a google drive using it's id",
    configs=[ConfigDownloadGoogleDrive],
)
def google_drive_download_by_id() -> None:
    """
    If you have a link to a google drive file like this:
    https://drive.google.com/open?id=0BwNoUKizWBdnRmRmLVlWSWxzWnM
    or like this:
    https://drive.google.com/file/d/0BwNoUKizWBdnSHF4SFlyRkxNSVE/view?usp=sharing
    Then the file id of the relevant files are:
    0BwNoUKizWBdnRmRmLVlWSWxzWnM
    0BwNoUKizWBdnSHF4SFlyRkxNSVE
    And this is what you have to supply to this script to download the files.

    References:
    - http://stackoverflow.com/questions/25010369/wget-curl-large-file-from-google-drive
    """
    download_file_from_google_drive(
        ConfigDownloadGoogleDrive.file_id,
        ConfigDownloadGoogleDrive.destination,
    )


@register_endpoint(
    description="Download a file shared from a google drive using a link",
    configs=[ConfigDownloadGdriveURL],
)
def google_drive_download_by_url() -> None:
    gdrive_download_link(url=ConfigDownloadGdriveURL.url)


@register_endpoint(
    description="Extension stats",
    allow_free_args=True,
)
def extension_stats():
    counter = collections.Counter()
    for filename in os.listdir():
        _, extension = os.path.splitext(filename)
        if len(extension) >= 1 and extension[0] == ".":
            extension = extension[1:]
        counter.update([extension])
    # pretty print the counter object
    total = 0
    for value, count in counter.most_common():
        print(f"{value} {count}")
        total += count
    print(f"total is {total}")


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    config_arg_parse_and_launch()


if __name__ == '__main__':
    main()
