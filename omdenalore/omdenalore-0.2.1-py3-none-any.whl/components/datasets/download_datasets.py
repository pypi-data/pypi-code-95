from tqdm import tqdm
import logging
import requests
import os

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def download_from_url(url, dst):
    """
    download dataset from a url

    :param url: url to download file
    :type url: str
    :param dst: destination place to put the file
    :type dst: str
    :returns: file size and saved datasets

    """
    req = requests.get(url, stream=True, verify=False)
    file_size = int(req.headers["Content-length"])
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    pbar = tqdm(
        total=file_size,
        initial=first_byte,
        unit="B",
        unit_scale=True,
        desc=url.split("/")[-1],
    )

    with (open(dst, "wb")) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)

    pbar.close()
    return file_size
