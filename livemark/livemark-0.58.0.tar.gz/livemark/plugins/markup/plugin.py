import marko
import textwrap
from pyquery import PyQuery
from marko.ext.gfm import GFM
from ..html.renderer import HtmlExtension
from ...plugin import Plugin


# NOTE:
# We might consider rebase markdown blocks rendering on using Document
# This change will remove the direct HtmlException and GFM dependencies


class MarkupPlugin(Plugin):
    identity = "markup"

    # Process

    def process_snippet(self, snippet):
        if self.document.format == "html":
            if snippet.type == "markup":
                if snippet.lang == "html":
                    markdown = marko.Markdown()
                    markdown.use(GFM)
                    markdown.use(HtmlExtension)
                    query = PyQuery(snippet.input)
                    for node in query.find(".livemark-markdown"):
                        node = PyQuery(node)
                        if not node.children():
                            input = node.text(squash_space=False)
                            input = textwrap.dedent(input).strip("\n")
                            output = markdown.convert(input)
                            node.html(output)
                    snippet.output = query.outer_html() + "\n"
