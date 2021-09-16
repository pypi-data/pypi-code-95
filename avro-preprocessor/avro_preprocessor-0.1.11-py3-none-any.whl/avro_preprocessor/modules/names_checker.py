"""
A module to check that every property ('name') has appropriate format.
"""
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.modules.avro_sorter import AvroSorter
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


@dataclass
class Schema:
    """
    Helper class to store schemas
    """
    name: str
    schema: str


class NamesChecker(PreprocessorModule):
    """
    Checks property name fields ('name').
    """
    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)

        self.current_schema_name: str = ""
        self.failure_due_to_naming = False
        self.current_docs: Dict[str, Schema] = {}

    def process(self) -> None:
        """Process all schemas."""

        for _, schema in self.processed_schemas_iter():
            self.traverse_schema(self.check_property_names, schema)

        if self.failure_due_to_naming:
            raise ValueError("Naming conventions are mandatory, see above for specific errors.")

    def check_property_names(self, schema: Avro.Node) -> None:
        """
        Checks that a (sub) schema complies with the property naming policy.

        :param schema: The (sub) schema
        """

        if not isinstance(schema, OrderedDict):
            return

        if Avro.Protocol in schema:
            if not self.is_camel_case(schema[Avro.Protocol]):
                self.failure_due_to_naming = True
                print(
                    'Error: schema "protocol" does not comply to policy (camel case):   ',
                    self.current_schema_name,
                    '   subschema: ', self.json_of(schema)
                )

        if Avro.Name in schema:
            if Avro.Type in schema and schema[Avro.Type] in (Avro.Record, Avro.Enum, Avro.Error):
                if not self.is_camel_case(schema[Avro.Name]):
                    self.failure_due_to_naming = True
                    print(
                        'Error: schema/record "name" does not comply to policy (camel case):   ',
                        self.current_schema_name,
                        '   subschema: ', self.json_of(schema)
                    )

            elif not self.is_snake_case(schema[Avro.Name]):
                self.failure_due_to_naming = True
                print(
                    'Error: sub-schema "name" property does not comply to policy (snake_case):   ',
                    self.current_schema_name,
                    '   subschema: ', self.json_of(schema)
                )

    @staticmethod
    def is_snake_case(string: str) -> bool:
        """
        Check if a string is snake_case.

        :param string: The string in input
        :return: bool
        """
        return string == string.lower()

    @staticmethod
    def is_camel_case(string: str) -> bool:
        """
        Check if a string is CamelCase.

        :param string: The string in input
        :return: bool
        """
        return '_' not in string

    @staticmethod
    def json_of(schema: OrderedDict) -> str:
        """
        Gets a compact, sorted JSON representation of a (sub) schema
        :param schema: The (sub) schema
        :return: The string representation
        """
        return json.dumps(AvroSorter.sort_avro(schema), indent=None)
