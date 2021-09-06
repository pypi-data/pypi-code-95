# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import os
import re
import requests
import sys
import time
from urllib.parse import urlparse

from tuxrun.utils import ProgressIndicator, NoProgressIndicator
from tuxrun.xdg import get_cache_dir


KERNELS = {
    "qemu-armv5": "https://storage.tuxboot.com/armv5/zImage",
    "qemu-armv7": "https://storage.tuxboot.com/armv7/zImage",
    "qemu-arm64": "https://storage.tuxboot.com/arm64/Image",
    "qemu-i386": "https://storage.tuxboot.com/i386/bzImage",
    "qemu-mips32": "https://storage.tuxboot.com/mips32/vmlinux",
    "qemu-mips32el": "https://storage.tuxboot.com/mips32el/vmlinux",
    "qemu-mips64": "https://storage.tuxboot.com/mips64/vmlinux",
    "qemu-mips64el": "https://storage.tuxboot.com/mips64el/vmlinux",
    "qemu-ppc32": "https://storage.tuxboot.com/ppc32/uImage",
    "qemu-ppc64": "https://storage.tuxboot.com/ppc64/vmlinux",
    "qemu-ppc64le": "https://storage.tuxboot.com/ppc64le/vmlinux",
    "qemu-riscv64": "https://storage.tuxboot.com/riscv64/Image",
    "qemu-sparc64": "https://storage.tuxboot.com/sparc64/vmlinux",
    "qemu-x86_64": "https://storage.tuxboot.com/x86_64/bzImage",
}


ROOTFS = {
    "qemu-armv5": "https://storage.tuxboot.com/armv5/rootfs.ext4.zst",
    "qemu-armv7": "https://storage.tuxboot.com/armv7/rootfs.ext4.zst",
    "qemu-arm64": "https://storage.tuxboot.com/arm64/rootfs.ext4.zst",
    "qemu-i386": "https://storage.tuxboot.com/i386/rootfs.ext4.zst",
    "qemu-mips32el": "https://storage.tuxboot.com/mips32el/rootfs.ext4.zst",
    "qemu-mips32": "https://storage.tuxboot.com/mips32/rootfs.ext4.zst",
    "qemu-mips64el": "https://storage.tuxboot.com/mips64el/rootfs.ext4.zst",
    "qemu-mips64": "https://storage.tuxboot.com/mips64/rootfs.ext4.zst",
    "qemu-ppc32": "https://storage.tuxboot.com/ppc32/rootfs.ext4.zst",
    "qemu-ppc64": "https://storage.tuxboot.com/ppc64/rootfs.ext4.zst",
    "qemu-ppc64le": "https://storage.tuxboot.com/ppc64le/rootfs.ext4.zst",
    "qemu-riscv64": "https://storage.tuxboot.com/riscv64/rootfs.ext4.zst",
    "qemu-sparc64": "https://storage.tuxboot.com/sparc64/rootfs.ext4.zst",
    "qemu-x86_64": "https://storage.tuxboot.com/x86_64/rootfs.ext4.zst",
}


TEST_DEFINITIONS = "https://storage.tuxboot.com/test-definitions/2021.04.tar.zst"


def get_rootfs(
    device, rootfs: str = None, progress: ProgressIndicator = NoProgressIndicator()
) -> str:
    return __download_and_cache__(rootfs or ROOTFS[device], progress)


def get_test_definitions(progress: ProgressIndicator = NoProgressIndicator()):
    return __download_and_cache__(TEST_DEFINITIONS, progress)


def __download_and_cache__(
    url: str, progress: ProgressIndicator = NoProgressIndicator()
):
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        return url

    key = re.sub(r"[:/]", "_", url)

    cache_dir = get_cache_dir().resolve() / "assets"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / key
    cache_etag_file = cache_dir / (key + ".etag")

    expired = False
    if cache.exists():
        timestamp = os.stat(cache).st_mtime
        now = time.time()
        timeout = 6 * 60 * 60  # 6 hours

        expired = (now - timestamp) > timeout
        if not expired:
            return str(cache)

    try:
        response = requests.get(url, allow_redirects=True, stream=True)
    except Exception as e:
        if cache.exists():
            print(e, "Continuing with cached version of the file", file=sys.stderr)
            return str(cache)
        else:
            raise e

    etag = str(response.headers["ETag"])
    if cache_etag_file.exists():
        cache_etag = cache_etag_file.read_text()
    else:
        cache_etag = None
    if cache_etag == etag:
        response.close()
        return str(cache)
    else:
        cache_etag_file.write_text(etag)

    size = int(response.headers.get("Content-Length", "0"))
    with cache.open("wb") as data:
        n = 0
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                n += data.write(chunk)
                if size:
                    progress.progress(100 * n / size)

    if size:
        progress.finish()

    return str(cache.resolve())
