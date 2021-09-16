"""The ou-sphinx-a11y package provides accessibility checking for Sphinx projects.

It is run via the "a11check" builder.
"""
import logging

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.dummy import DummyBuilder
from sphinx.util.console import darkgray, darkgreen, purple, red, turquoise  # type: ignore
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util.nodes import get_node_line
from typing import (Any, Dict, Generator, List, NamedTuple, Optional, Pattern, Set, Tuple,
                    Union, cast)


logger = logging.getLogger('sphinx.ext.builders.ou.a11ycheck')


class A11yBuilder(DummyBuilder):
    """The A11yBuilder performs accessibility checks."""

    name = 'a11ycheck'

    def init(self) -> None:
        self.images: List[Tuple(str, int, nodes.image)] = []

    def log_error(self, docname: str, lineno: int, msg: str) -> None:
        if self.app.quiet or self.app.warningiserror:
            logger.warning(red('ERROR   ') + docname + ':' + str(lineno) + ' - ' + msg)
        else:
            logger.info(red('ERROR   ') + docname + ':' + str(lineno) + ' - ' + msg)

    def log_warning(self, docname: str, lineno: int, msg: str) -> None:
        if self.app.quiet or self.app.warningiserror:
            logger.warning(turquoise('WARNING ') + docname + ':' + str(lineno) + ' - ' + msg)
        else:
            logger.info(turquoise('WARNING ') + docname + ':' + str(lineno) + ' - ' + msg)

    def finish(self) -> None:
        is_valid = True
        for docname, lineno, image in self.images:
            if 'alt' in image.attributes:
                if image.attributes['alt'].strip() == '':
                    self.log_warning(docname, lineno, 'Alt attribute is empty')
            else:
                is_valid = False
                self.log_error(docname, lineno, 'Missing alt attribute')
        if not is_valid:
            self.app.statuscode = 1


class ImageCollector(SphinxPostTransform):

    builders = ('a11ycheck',)
    default_priority = 800

    def run(self, **kwargs: Any) -> None:
        builder = cast(A11yBuilder, self.app.builder)
        images = builder.images
        for imagenode in self.document.traverse(nodes.image):
            lineno = get_node_line(imagenode)
            exists = False
            for tmp in images:
                if tmp[0] == self.env.docname and tmp[1] == lineno:
                    exists = True
                    break
            if not exists:
                images.append((self.env.docname, lineno, imagenode))


def setup(app: Sphinx):
    """Setup the OU Sphinx theme and extensions."""
    app.add_builder(A11yBuilder)
    app.add_post_transform(ImageCollector)
    return {'parallel_read_safe': False, 'parallel_write_safe': False}
