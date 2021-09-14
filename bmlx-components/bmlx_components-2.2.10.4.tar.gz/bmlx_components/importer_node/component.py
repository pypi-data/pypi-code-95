from bmlx_components.importer_node.driver import ImporterDriver
from bmlx.flow import Node, Artifact, Channel
from bmlx.flow.driver_spec import DriverClassSpec
from typing import Union, List, Text, Type, Optional, Dict, Any


class ImporterNode(Node):
    DRIVER_SPEC = DriverClassSpec(ImporterDriver)

    def __init__(
        self,
        instance_name,
        source_uri: Union[Text, List[Text]],
        artifact_type: Type[Artifact],
        reimport: Optional[bool] = False,
        import_checker: Optional[Text] = "check_uri_exist",
        try_limit: int = 1,
    ):
        self._source_uri = (
            source_uri if isinstance(source_uri, list) else [source_uri]
        )
        self._reimport = reimport
        self._import_checker = import_checker

        self._output_dict = {
            "result": Channel(
                artifact_type=artifact_type, artifacts=[artifact_type()]
            )
        }
        super(ImporterNode, self).__init__(
            instance_name=instance_name, try_limit=try_limit
        )

    def __repr__(self):
        return "ImporterNode: name:%s uri:%s" % (
            self._instance_name,
            self._source_uri,
        )

    def to_json_dict(self) -> Dict[Text, Any]:
        return {
            "instance_name": self._instance_name,
            "output_dict": self._output_dict,
            "reimport": self._reimport,
            "source_uri": self._source_uri,
            "driver_spec": self.driver_spec,
            "executor_spec": self.executor_spec,
            "import_checker": self._import_checker,
        }

    @property
    def inputs(self) -> Dict[str, Channel]:
        return {}

    @property
    def outputs(self) -> Dict[str, Channel]:
        return self._output_dict

    @property
    def exec_properties(self) -> Dict[Text, Any]:
        return {
            "source_uri": self._source_uri,
            "reimport": self._reimport,
            "import_checker": self._import_checker,
        }

    @property
    def try_limit(self) -> int:
        return self._try_limit
