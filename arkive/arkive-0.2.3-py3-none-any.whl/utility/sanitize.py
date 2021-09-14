from pathlib import Path
from pathvalidate import sanitize_filename, sanitize_filepath


def sanitize_name(name: str) -> str:
    new_name = sanitize_filename(name)
    return "BLANK" if new_name is "" else new_name


def sanitize_path(path: Path) -> Path:
    if not isinstance(path, Path):
        raise ValueError
    return sanitize_filepath(path, platform='auto')
