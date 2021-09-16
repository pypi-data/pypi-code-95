import markdown

from stag.ecs import Page, Path, Content


def add_md_file(site, text, metadata=None, parse=False):
    if metadata is None:
        metadata = {}

    config = site.config
    html = markdown.markdown(text) if parse else None
    f = Page(
        url="/page",
        source=Path("page/index.md", site.config.content),
        metadata=metadata,
        input=Content("md", text),
        output=Content("html", html),
    )

    site.pages.add(f)
    return f


def contents(path):
    with open(path) as file:
        return file.read().strip()
