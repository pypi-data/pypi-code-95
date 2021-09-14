from bmlx_components.xdl_base.launcher import XdlLauncher


class XdlEvalLauncher(XdlLauncher):
    def _need_ps(self):
        return True

    def _need_passive_quit(self):
        return True

    def _need_launch_xdl(self, input_dict, exec_properties):
        if (("model" not in input_dict or not input_dict["model"]) 
        and ("specific_model" not in exec_properties or not exec_properties["specific_model"])):
            return False
        return True

    def _stage(self):
        return "eval"
