import os
import shutil

from .base import reader, writer
from stag.ecs import Page


class CopyError(Exception):
    pass


def write_cnd(page):
    return page.source and not page.input


@reader("static")
def read(path, site):
    def strip_roots(url):
        opj = os.path.join
        c = site.config
        excls = ["static", opj(c.plugins.theme.name, "static"), c.content]
        for ex in excls:
            if url.startswith(ex):
                return url[len(ex) :].strip("/")
        return url.strip("/")

    url = path.relpath
    return Page(url=f"/{url}", source=path)


@writer("copy", cond=write_cnd)
def write(page, site):
    url = page.url.strip("/")
    output_path = os.path.join(site.config.output, url)

    if os.path.exists(output_path):
        raise CopyError(f"File exists: {output_path}")

    target_dir = os.path.dirname(output_path)
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(page.source.path, target_dir)
