from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from arkive.core.drive import Drive
from arkive.utility.sanitize import sanitize_path, sanitize_name


def nest_music_file(drive: Drive, file: dict, destination: Path):
    artist, album, title = (sanitize_name(file[name]) for name in ['artist', 'album', 'title'])

    filepath = (destination / artist / album / title).with_suffix(file['path'].suffix)
    output = sanitize_path(filepath)

    drive.rename(file['path'], output)


def nest_music_collection(drive: Drive, origin: Path, destination: Path):
    # for file in drive.index(origin):
    #     nest_music_file(drive, file, destination)
    with ThreadPoolExecutor() as executor:
        executor.map(lambda file: nest_music_file(drive, file, destination), drive.index(origin))
    drive.cleanup(origin)
