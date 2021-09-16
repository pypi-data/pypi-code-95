"""
Class to define input and output paths for Avro schema directory trees.
"""

import glob
import shutil
from pathlib import Path
from typing import Callable, Optional, List

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class AvroPaths:  # pylint: disable=R0902
    """Class for keeping track of Avro schemas path."""

    def __init__(
            self,
            input_path: str,
            output_path: str,
            base_namespace: str,
            types_namespace: Optional[str] = None,
            rpc_namespace: Optional[str] = None,
            metadata_schema: Optional[str] = None,
            metadata_exclude: Optional[List[str]] = None,
            key_schema: Optional[str] = None,
            key_subject_name_strategy: str = "TopicRecordNameStrategy",
            input_schema_file_extension: str = 'exavsc',
            output_schema_file_extension: str = 'avsc',
            input_schema_file_format: str = 'json',
            output_schema_file_format: str = 'json',
            schema_mapping_path: Path = Path('./schema-mapping.json'),
            schema_mapping_exclude: Optional[List[str]] = None,
            schema_mapping_user_id_types_exclude: Optional[List[str]] = None,
            avro_tools_path: Optional[str] = None
    ):  # pylint: disable=R0913
        """
        :param input_path: The root input path
        :param output_path: The root output path
        :param base_namespace: The root namespace for schemas (e.g. 'com.example')
        :param types_namespace: The namespace of types (reusable schemas not registered to a topic)
        :param rpc_namespace: The namespace of rpc protocols
        :param metadata_schema: The fully qualified name of the metadata type schema
        :param key_schema: The fully qualified name of the key type schema
        :param input_schema_file_extension: The filename extension of input Avro files
        :param output_schema_file_extension: The filename extension of output Avro files
        :param input_schema_file_format: The format of input Avro files
        :param output_schema_file_format: The format of output Avro files
        :param schema_mapping_path: The path of the schema mapping JSON file
        :param schema_mapping_exclude: The paths excluded from the schema mapping
        :param schema_mapping_user_id_types_exclude: The containers (e.g. array or map) to exclude
        :param avro_tools_path: The path to the Avro tools jar
        """
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.base_namespace: str = base_namespace
        self.types_namespace: Optional[str] = types_namespace
        if self.types_namespace and not self.types_namespace.startswith(self.base_namespace):
            raise ValueError("Types namespace {} should be part of base namespace {}."
                             .format(self.types_namespace, self.base_namespace))
        self.rpc_namespace: Optional[str] = rpc_namespace
        if self.rpc_namespace and not self.rpc_namespace.startswith(self.base_namespace):
            raise ValueError("RPC namespace {} should be part of base namespace {}."
                             .format(self.rpc_namespace, self.base_namespace))
        self.metadata_schema: Optional[str] = metadata_schema
        self.metadata_exclude: List[str] = metadata_exclude if metadata_exclude else []
        self.key_schema: Optional[str] = key_schema
        self.key_subject_name_strategy: str = key_subject_name_strategy
        self.input_schema_file_extension: List[str] = \
            input_schema_file_extension.replace('.', '').split(',')
        self.output_schema_file_extension: str = output_schema_file_extension.replace('.', '')
        self.input_schema_file_format = input_schema_file_format
        self.output_schema_file_format = output_schema_file_format
        self.schema_mapping_path: Path = schema_mapping_path
        self.schema_mapping_exclude: List[str] = \
            schema_mapping_exclude if schema_mapping_exclude else []
        self.schema_mapping_user_id_types_exclude: List[str] = \
            schema_mapping_user_id_types_exclude if schema_mapping_user_id_types_exclude else []
        self.avro_tools_path: Optional[str] = avro_tools_path

    def to_output_path(self, name: str) -> Path:
        """
        Schema fully qualified name to output path
        :param name: schema name
        :return: the output path
        """
        return Path(self.output_path).joinpath(Path(name.replace('.', '/'))) \
            .with_suffix('.' + self.output_schema_file_extension)

    def to_input_path(self, name: str, extension: str) -> Path:
        """
        Schema fully qualified name to input path
        :param name: schema name
        :param extension: schema extension
        :return: the input path
        """
        return Path(self.input_path).joinpath(Path(name.replace('.', '/'))) \
            .with_suffix('.' + extension)

    def is_type_resource(self, schema_namespace: str) -> bool:
        """
        Returns True if a schema namespace is type, i.e. it is a reusable Avro resource
        not to be registered to a Kafka topic.
        :param schema_namespace: The namespace of this schema
        :return: bool
        """
        if self.types_namespace is not None and schema_namespace.startswith(self.types_namespace):
            return True

        return False

    def is_rpc_resource(self, schema_namespace: str) -> bool:
        """
        Returns True if a schema namespace is a rpc resource, i.e. it is an Avro resource
        for RPC protocol communications.
        :param schema_namespace: The namespace of this schema
        :return: bool
        """
        if self.rpc_namespace is not None and schema_namespace.startswith(self.rpc_namespace):
            return True

        return False

    def is_event_resource(self, schema_namespace: str) -> bool:
        """
        Returns True if a schema namespace is an event schema resource.
        :param schema_namespace: The namespace of this schema
        :return: bool
        """
        if self.is_type_resource(schema_namespace) or self.is_rpc_resource(schema_namespace):
            return False

        return True

    @staticmethod
    def traverse_path(root_path: str, file_extension: List[str], func: Callable[[Path], None]) \
            -> None:
        """
        Traverse a path and applies 'func' to each file matching the extension in input.
        :param root_path: The root path
        :param file_extension: The extension to match
        :param func: The function to apply
        """
        for file in glob.iglob(root_path + '/**/*', recursive=True):
            path = Path(file).resolve()
            if path.suffix.replace('.', '') in file_extension:
                func(path)

    @staticmethod
    def reset_directory(directory: str) -> None:
        """
        Deletes and re-creates a directory
        :param directory: The directory
        """
        shutil.rmtree(directory, ignore_errors=True)
        Path(directory).parent.mkdir(parents=True, exist_ok=True)
