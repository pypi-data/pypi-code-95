from bmlx_components.xdl_base.launcher import XdlLauncher


class XdlConverterLauncher(XdlLauncher):
    def _need_ps(self):
        return False

    def _need_passive_quit(self):
        return False

    def _need_launch_xdl(self, input_dict, exec_properties):
        return True

    def _stage(self):
        return "convert"

    def _add_specific_exec_properties(self, exec_properties):
        pass
