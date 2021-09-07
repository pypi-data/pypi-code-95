import os

from pydmt.api.feature import Feature
from pydmt.builders.sphinx import Sphinx
from pydmt.core.pydmt import PyDMT


class Documentation(Feature):
    def __init__(
        self,
        sphinx_folder: str = "sphinx",
    ):
        self.sphinx_folder = sphinx_folder
        # pylint: disable=import-outside-toplevel
        try:
            import config.project
            self.project_name = config.project.project_name
        except ModuleNotFoundError:
            pass

    def setup(self, pydmt: PyDMT) -> None:
        if not os.path.isdir(self.sphinx_folder):
            return
        pydmt.add_builder(Sphinx(package_name=self.project_name))
