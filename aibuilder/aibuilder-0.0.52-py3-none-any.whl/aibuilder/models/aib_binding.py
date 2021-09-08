import json
from enum import Enum
from typing import Dict

from aibuilder.models.constants import AIBBindingConstants
from aibuilder.models.exceptions import DataBindingValidationException


class AIBDataType(Enum):
    """
    AI Builder data types

    """
    boolean = "Boolean"
    string = "String"
    decimal = "Decimal"
    integer = "Integer"


class AIBSpecification(Enum):
    """
    AI Builder specification types

    """
    prediction = "Prediction"
    likelihood = "Likelihood"
    explanation = "Explanation"


class AIBTableBinding:
    """
    Class to bind Dataverse Table columns with AI Model

    """

    def __init__(self, table_name: str, column_bindings: dict):
        """
        Initializing AIBTableBinding class with DataVerse Table name and Column bindings dictionary

        :param table_name: Logical name of DataVerse Table
        :param column_bindings: Dictionary with Model column name as key and DataVerse Column as value
        """
        if not isinstance(table_name, str):
            raise TypeError(f"Table name should be of type string, got: {type(table_name)}")
        if not isinstance(column_bindings, dict):
            raise TypeError(f"Column bindings should be of type dict, got: {type(column_bindings)}")

        self._table_name = table_name
        self._column_bindings = column_bindings

    @property
    def table_name(self) -> str:
        """
        Returns table name

        """
        return self._table_name

    @property
    def column_bindings(self) -> dict:
        """
        Returns column bindings

        """
        return self._column_bindings


class AIBBinding:
    """
    Class to bind input DataVerse Table and output DataVerse Table with AI Builder

    """

    def __init__(self,
                 input_binding: AIBTableBinding,
                 output_binding: AIBTableBinding,
                 specification: dict = None
                 ):
        """
        Initializing AIB Binding class with input table binding and output table binding

        :param input_binding: Input Table Binding
        :param output_binding: Output Table Binding
        :param specification: Optional dictionary mapping model column to AI Builder Specification
        """
        if not isinstance(input_binding, AIBTableBinding) or not isinstance(output_binding, AIBTableBinding):
            raise ValueError(f"Input and output binding parameters should be instance of AIBTableBinding, got: "
                             f"{type(input_binding)} and {type(output_binding)}")

        self._input_binding = input_binding
        self._output_binding = output_binding

        if specification is None:
            self._specification = {}

        self._output_column_types = {}
        self._binding = None

    @property
    def binding(self) -> str:
        """
        Returns AI Builder data binding json constructed using class instance attributes

        """
        return json.dumps(self._get_data_binding())

    def set_output_column_types(self, output_column_types: Dict[str, AIBDataType]) -> None:
        """
        Set model output column types which will be used to generate data binding.

        :param output_column_types: Dictionary with model output fields as key and AIBDataType as value
        :return: None
        """
        if not isinstance(output_column_types, dict):
            TypeError(f"Output column types should be a dictionary, but got: {type(output_column_types)}")
        # check if all dictionary values are of type AIBDataType
        if all(map(lambda v: isinstance(v, AIBDataType), output_column_types.values())):
            ValueError(f"Output column types dictionary values should be of type AIBDataType, "
                       f"got: {map(lambda x: type(x), output_column_types.values())}")

        self._output_column_types = output_column_types

    def _get_data_binding(self) -> dict:
        """
        Constructs data binding using AIBBinding attributes

        """
        if len(self._output_column_types) == 0:
            raise ValueError("Output column types are not set. "
                             "Use set_output_column_types method to set output column types")

        if self._binding is None:
            input_attributes = AIBBinding._get_input_attributes(self._input_binding)
            output_attributes = AIBBinding._get_output_attributes(self._output_binding, self._output_column_types)

            self._binding = {
                AIBBindingConstants.schema_version_key.value: AIBBindingConstants.schema_version.value,
                AIBBindingConstants.schema_input.value: {
                    AIBBindingConstants.schema_name.value: self._input_binding.table_name,
                    AIBBindingConstants.attributes.value: input_attributes
                },
                AIBBindingConstants.schema_output.value: {
                    AIBBindingConstants.schema_name.value: self._output_binding.table_name,
                    AIBBindingConstants.attributes.value: output_attributes
                }
            }

        return self._binding

    def _validate(self, aib_data_specification: str) -> bool:
        """
        Check if input or output data type is an image. As image input types are not supported by AI Builder
        for batch prediction.
        :param aib_data_specification: Data specification
        :return: True if all validation passes else returns False
        """
        aib_data_specification_dict = json.loads(aib_data_specification)

        columns_with_input_type_image = []
        for attribute in aib_data_specification_dict["input"].get("attributes", []):
            if attribute.get("dataType") == "Image":
                columns_with_input_type_image.append(attribute["displayName"])

        if len(columns_with_input_type_image) > 0:
            raise DataBindingValidationException(f"Data binding is not supported for Image input types."
                                                 f"Found columns with Image types: {columns_with_input_type_image}")
        return True

    @classmethod
    def _get_input_attributes(cls, input_binding: AIBTableBinding) -> list:
        """
        Constructs input attributes using input table bindings

        :param input_binding: AIBTableBinding object mapping DataVerse input table and model input fields
        :return: Formatted input attributes list
        """
        input_attributes = []

        for model_column in input_binding.column_bindings:
            attribute = {
                AIBBindingConstants.specification_name.value: model_column,
                AIBBindingConstants.schema_name.value: input_binding.column_bindings[model_column]
            }
            input_attributes.append(attribute)

        return input_attributes

    @classmethod
    def _get_output_attributes(cls, output_binding: AIBTableBinding, output_column_types: dict) -> list:
        """
        Constructs output attributes using output table bindings and output column types dictionary

        :param output_binding: AIBTableBinding object mapping DataVerse output table and model output
        :param output_column_types: Dictionary with model output fields as key and AIBDataType as value
        :return: Formatted output attributes list
        """
        output_attributes = []

        for output_column in output_binding.column_bindings:
            attribute = {
                AIBBindingConstants.schema_name.value: output_binding.column_bindings[output_column],
                AIBBindingConstants.display_name.value: output_column,
                AIBBindingConstants.specification_name.value: output_column,
                AIBBindingConstants.data_type.value: output_column_types.get(output_column).value
            }
            output_attributes.append(attribute)

        return output_attributes
