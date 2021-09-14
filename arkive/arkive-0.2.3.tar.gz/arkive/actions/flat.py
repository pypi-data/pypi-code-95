from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from arkive.core.drive import Drive
from arkive.utility.sanitize import sanitize_path, sanitize_name


def flat_music_file(drive: Drive, file: dict, destination: Path):
    artist, album, title = (sanitize_name(file[name]) for name in ['artist', 'album', 'title'])

    name = f'{artist} - {album} - {title}'
    filepath = (destination / name).with_suffix(file['path'].suffix)
    output = sanitize_path(filepath)

    drive.rename(file['path'], output)


def flat_music_collection(drive: Drive, origin: Path, destination: Path):
    # for file in drive.index(origin):
    #     flat_music_file(drive, file, destination)
    with ThreadPoolExecutor() as executor:
        executor.map(lambda file: flat_music_file(drive, file, destination), drive.index(origin))
    drive.cleanup(origin)
