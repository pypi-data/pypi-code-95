from pathlib import Path
import typing as T
import logging

def get(path: Path, recurse: bool = False) -> T.Iterable[Path]:
    """
    yield files in path with suffix ext. Optionally, recurse directories.
    """
    path = Path(path).expanduser().resolve()
    if path.is_dir():
        for p in path.iterdir():
            if p.is_file():
                yield p
            elif p.is_dir():
                if recurse:
                    yield from get(p, recurse)
    elif path.is_file():
        logging.debug(f'Adding file to be checked: {path}')
        yield path
    else:
        raise FileNotFoundError(path)
