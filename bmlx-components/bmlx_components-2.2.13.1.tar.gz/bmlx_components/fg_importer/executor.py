import os
import logging
from typing import Text, Dict, List, Any
from bmlx.flow import Executor, Artifact
from bmlx.utils import io_utils
from bmlx_components import custom_artifacts

class FgImporterExecutor(Executor):
    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        assert len(input_dict) <= 1
        
        #当fg_importer定义了fg_conf_input时，用fg_conf_input的uri覆盖可能存在的fg_conf的路径
        if len(input_dict) == 1:
            assert len(output_dict["fg_conf"]) == 1

            fg_conf_input_path = input_dict["fg_conf_input"][0].meta.uri
            assert io_utils.exists(fg_conf_input_path)

            componet_id = output_dict["fg_conf"][0].meta.producer_component
            artifact = Artifact(
                type_name=custom_artifacts.FgConf.TYPE_NAME
            )
            artifact.meta.uri = fg_conf_input_path
            artifact.meta.producer_component = componet_id
            artifact.meta.import_only = True

            output_dict["fg_conf"] = [artifact]

        else:
            logging.debug("input_dict len != 1")