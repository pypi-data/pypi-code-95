import argh
from typing import Iterator
from unicodedata import normalize
import os
import re
from jama_client import Client, IncompleteUpload, AlreadyUploaded


def _secure_filename(filename: str) -> str:
    filename = normalize("NFKD", filename).encode("ascii", "ignore")
    filename = filename.decode("ascii")
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    _filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )
    return filename


def _print(msg: str, verbose: bool = True):
    if verbose:
        print(msg)


def _scan_dir(start_path: str, extension: str = None) -> Iterator[str]:
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if extension:
                if file[(len(extension) * -1) :].lower() == extension.lower():
                    yield os.path.join(root, file)
            else:
                yield os.path.join(root, file)


def upload(
    start_dir: str, endpoint: str = None, api_key: str = None, verbose: bool = False
):
    if api_key is None:
        api_key = os.getenv("JAMA_API_KEY", None)
    if not api_key:
        raise ValueError("Missing JAMA_API_KEY")
    if endpoint is None:
        endpoint = os.getenv("JAMA_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Missing JAMA_ENDPOINT")

    _print("Uploading {} to {}".format(start_dir, endpoint), verbose)
    client = Client(endpoint, api_key)
    if not os.path.isdir(start_dir):
        raise ValueError("Not a directory")
    if start_dir[-1] == "/":
        start_dir = start_dir[0:-1]
    base_dir_name = start_dir.split("/")[-1]
    for path in _scan_dir(start_dir):
        dir_name = "".join([base_dir_name, os.path.dirname(path[len(start_dir) :])])
        try:
            client.upload(path, origin_dir_name=dir_name)
            _print("Uploaded: {}".format(os.path.basename(path)), verbose)
        except IncompleteUpload:
            _print("Incomplete: {}".format(os.path.basename(path)), verbose)
        except AlreadyUploaded:
            _print("Skipped: {}".format(os.path.basename(path)), verbose)


def run_cli():
    parser = argh.ArghParser()
    parser.add_commands([upload])
    parser.dispatch()


if __name__ == "__main__":
    run_cli()
