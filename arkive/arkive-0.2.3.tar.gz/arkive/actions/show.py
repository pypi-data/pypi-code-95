from pathlib import Path

from arkive.core.drive import Drive


def show_music_file(file: dict):
    return [file['artist'], file['album'], file['title']]


def show_music_collection(drive: Drive, origin: Path):
    content = []
    for file in drive.index(origin):
        item_row = show_music_file(file)
        content.append(item_row)
    return ['ARTIST', 'ALBUM', 'TITLE'], content
