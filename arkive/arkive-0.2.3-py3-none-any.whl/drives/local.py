from pathlib import Path
from tinytag import TinyTag, TinyTagException

from arkive.core.drive import Drive


def _local_metadata(item, track):
    return {'artist': track.artist, 'album': track.album, 'title': track.title, 'path': item}


def _local_index(folder: Path):
    for item in folder.rglob('*'):
        if item.is_file():
            try:
                track = TinyTag.get(item)
                yield _local_metadata(item, track)
            except TinyTagException:
                pass


def _local_rename(file: Path, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    file.replace(output)


def _local_folder_remove(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        pass


def _local_folder_cleanup(folder: Path):
    for item in folder.glob("*"):
        if item.is_dir():
            _local_folder_cleanup(item)
            _local_folder_remove(item)


class LocalDrive(Drive):
    def index(self, folder: Path):
        assert folder.exists() and folder.is_dir(), \
            f'\'{folder}\' is not a directory.'
        yield from _local_index(folder)

    def rename(self, source: Path, dest: Path):
        _local_rename(source, dest)

    def cleanup(self, folder: Path):
        _local_folder_cleanup(folder)
