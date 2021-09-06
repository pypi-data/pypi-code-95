"""
reStructuredText parser for rich

Gotten from: https://github.com/willmcgugan/rich/discussions/1263#discussioncomment-808898
There are some improvements are added by me
"""

# Imports from docutils package for the parsing
import docutils.io
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
# Imports from the rich package for the printing
from rich import box
import rich
from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.jupyter import JupyterMixin
from rich.panel import Panel
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text


# pylama:ignore=D,C0116
class RSTVisitor(docutils.nodes.SparseNodeVisitor):
    """A visitor that produces rich renderables"""
    def __init__(self, document: docutils.nodes.document) -> None:
        super().__init__(document)
        self.renderables = []
        self.supercript = str.maketrans("1234567890", "¹²³⁴⁵⁶⁷⁸⁹⁰")
        self.subscript = str.maketrans("1234567890", "₁₂₃₄₅₆₇₈₉₀")

    def depart_paragraph(self, node):  # pylint: disable=unused-argument
        self.renderables.append(Text("\n"))

    def visit_title(self, node):
        self.renderables.append(Panel(Align(node.astext(), "center"), box=box.DOUBLE, style="bold"))
        raise docutils.nodes.SkipChildren()

    def visit_Text(self, node):
        self.renderables.append(Text(node.astext(), end=""))

    def visit_attention(self, node):
        self.renderables.append(Text("Attention: " + node.astext(), style="bold white"))
        raise docutils.nodes.SkipChildren()

    def visit_caution(self, node):
        self.renderables.append(Text("Caution: " + node.astext(), style="red"))
        raise docutils.nodes.SkipChildren()

    def visit_danger(self, node):
        self.renderables.append(Text("DANGER: " + node.astext(), style="bold red"))
        raise docutils.nodes.SkipChildren()

    def visit_error(self, node):
        self.renderables.append(Text("ERROR: " + node.astext(), style="bold red"))
        raise docutils.nodes.SkipChildren()


    def visit_hint(self, node):
        self.renderables.append(Text("Hint: " + node.astext(), style="yellow"))
        raise docutils.nodes.SkipChildren()

    def visit_important(self, node):
        self.renderables.append(Text("IMPORTANT: " + node.astext(), style="bold blue"))
        raise docutils.nodes.SkipChildren()

    def visit_note(self, node):
        self.renderables.append(Text("Note: " + node.astext(), style="bold white"))
        raise docutils.nodes.SkipChildren()

    def visit_tip(self, node):
        self.renderables.append(Text("Tip: " + node.astext(), style="bold green"))
        raise docutils.nodes.SkipChildren()

    def visit_warning(self, node):
        self.renderables.append(Text("Warning: " + node.astext(), style="bold yellow"))
        raise docutils.nodes.SkipChildren()

    def visit_emphasis(self, node):
        self.renderables.append(Text(node.astext(), style="italic", end=""))
        raise docutils.nodes.SkipChildren()

    def visit_subscript(self, node):
        self.renderables.append(Text(node.astext().translate(self.subscript), end=""))
        raise docutils.nodes.SkipChildren()

    def visit_superscript(self, node):
        self.renderables.append(Text(node.astext().translate(self.supercript), end=""))
        raise docutils.nodes.SkipChildren()

    def visit_strong(self, node):
        self.renderables.append(Text(node.astext(), style="bold", end=""))
        raise docutils.nodes.SkipChildren()


    def visit_image(self, node):
        target = None
        if ":target:" in node.rawsource:
            target = node.rawsource.split(":target:")[-1]
        self.renderables.append(
            Text("🌆 ") + Text(node["alt"], style=Style(link=target or node.get("uri"), color="#6088ff"))
        )

    def visit_bullet_list(self, node):
        for list_item in node.children:
            self.renderables.append(Text(" • ", end="", style="bold yellow"))
            self.renderables.append(Text(list_item.astext()))

        self.renderables.append(Text())
        raise docutils.nodes.SkipChildren()

    def visit_enumerated_list(self, node):
        for i, list_item in enumerate(node.children, 1):
            self.renderables.append(Text(f"{i}. ", end=""))
            self.renderables.append(Text(list_item.astext()))

        self.renderables.append(Text())
        raise docutils.nodes.SkipChildren()

    def visit_literal(self, node):
        self.renderables.append(Text(node.astext(), style=Style(bgcolor="black", color="bright_white"), end=""))
        raise docutils.nodes.SkipChildren()

    def visit_literal_block(self, node):
        lexer = node["classes"][1] if len(node["classes"]) >= 2 else "python"
        self.renderables.append(Panel(Syntax(node.astext(), lexer), border_style="dim", box=box.SQUARE))
        raise docutils.nodes.SkipChildren()




class RestructuredText(JupyterMixin):
    """A reStructuredText renderable for rich."""

    def __init__(self, markup: str) -> None:
        """A reStructuredText renderable for rich.

        Parameters
        ----------
        markup : str
            A string containing reStructuredText markup.
        """
        self.markup = markup


    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        # Parse the `markup` into a RST `document`.
        option_parser = docutils.frontend.OptionParser(components=(docutils.parsers.rst.Parser,))
        settings = option_parser.get_default_values()
        source = docutils.io.StringInput(self.markup)
        document = docutils.utils.new_document(source.source_path, settings)
        rst_parser = docutils.parsers.rst.Parser()
        rst_parser.parse(source.read(), document)

        # Render the RST `document` using Rich.
        visitor = RSTVisitor(document)
        document.walkabout(visitor)

        for renderable in visitor.renderables:
            yield from console.render(renderable, options)

RST = ReStructuredText = reStructuredText = RestructuredText
