import logging
from bmlx.utils import artifact_utils, io_utils
from bmlx_components.xdl_base.driver import XdlDriver


class XdlTrainerDriver(XdlDriver):
    # override super method
    def _rewrite_launch_config(self, exec_properties):
        pass

    # override XdlDriver method
    def _resolve_model_paths(self, input_dict, exec_properties):
        model_uri = ""
        if "previous_model" in input_dict:
            if len(input_dict["previous_model"]) > 0:
                model_uri = artifact_utils.get_single_uri(
                    input_dict["previous_model"]
                )

        if "model_file_pattern" not in exec_properties:
            raise RuntimeError("model file pattern must set")

        warmup_opened = False
        # 如果选到了基础模型，则使用基础模型
        if model_uri:
            model_bank_uri = self._get_model_bank_uri(
                model_uri, exec_properties["model_file_pattern"]
            )
            warmup_opened = False
        # 如果没有基础模型，且设置了 warmup_model_bank
        elif exec_properties.get("warmup_model_bank"):
            warmups = exec_properties["warmup_model_bank"].split("@")
            if len(warmups) == 2 and io_utils.exists(warmups[1]):
                model_bank_uri = exec_properties["warmup_model_bank"]
                warmup_opened = True
        else:
            model_bank_uri = ""
            warmup_opened = False

        logging.info(
            "warmup %s, selected model bank uri: %s",
            "opened" if warmup_opened else "closed",
            model_bank_uri,
        )
        return model_bank_uri, exec_properties.get("model_uri_base", "")
