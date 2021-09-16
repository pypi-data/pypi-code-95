import os

import attr
import tomli
import markdown

from .base import reader, generator
from stag.ecs import Page, Content, Metadata


def is_md(path):
    return path.ext == "md"


def is_opened_md(page):
    return page.input and page.input.type == "md"


@attr.s(auto_attribs=True)
class MarkdownConfig:
    extensions: list[str] = ["footnotes", "fenced_code", "smarty"]


def deduce_url(path):
    if path.filebase == "index":
        return path.reldirname
    return os.path.join(path.reldirname, path.filebase)


@reader("markdown", cond=is_md)
def read(path, site):
    frontmatter = "+++"

    frontmatter_parsed = False
    in_frontmatter = False
    metadata = []
    content = []

    with open(path.path) as fd:
        for line in fd:
            line = line.rstrip("\r\n")
            if line == frontmatter:
                if not frontmatter_parsed:
                    frontmatter_parsed = True
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    in_frontmatter = False
                    continue

            if in_frontmatter:
                metadata.append(line)
            else:
                content.append(line)

    metadata_parsed = tomli.loads("\n".join(metadata))
    content_parsed = "\n".join(content)

    url = deduce_url(path)
    metadata = Metadata(metadata_parsed)
    input_ = Content("md", content_parsed)
    return Page(url=url, source=path, metadata=metadata, input=input_)


@generator("markdown", cond=is_opened_md, config=MarkdownConfig())
def generate(page, site):
    myconfig = site.config.plugins.markdown

    assert "title" in page.metadata, f"No title in {page.source.relpath}"

    extensions = myconfig.extensions
    html = markdown.markdown(page.input.content, extensions=extensions)
    page.output = Content("html", html)
