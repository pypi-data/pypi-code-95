from bmlx_components.xdl_base.launcher import XdlLauncher


class XdlPredictorLauncher(XdlLauncher):
    def _need_ps(self):
        return True

    def _need_passive_quit(self):
        return True

    def _need_launch_xdl(self, input_dict, exec_properties):
        return True

    def _stage(self):
        return "predict"
