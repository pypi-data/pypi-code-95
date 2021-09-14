import logging
from bmlx_components.xdl_base.launcher import XdlLauncher
from bmlx.utils import artifact_utils


class XdlTrainerLauncher(XdlLauncher):
    def _need_ps(self):
        return True

    def _need_passive_quit(self):
        return True

    def _need_launch_xdl(self, input_dict, exec_properties):
        return True

    def _stage(self):
        return "train"
