import io
import zipfile
from pathlib import Path

import requests

default_url = "https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip"
default_file_name = "KEN_ALL.CSV"
default_output_dir = Path.home().joinpath(".local/jpaddressparser/")


def download_csv(
    url=default_url,
    file_name=default_file_name,
    output_directory: Path = default_output_dir,
):
    resp = requests.get(default_url)
    fp = io.BytesIO(resp.content)
    fp.seek(0)
    zfp = zipfile.ZipFile(fp, "r")
    data = zfp.read(file_name)

    if not output_directory.exists():
        output_directory.mkdir()

    with output_directory.joinpath(file_name).open("wb") as ofp:
        ofp.write(data)


if __name__ == "__main__":
    download_csv()
