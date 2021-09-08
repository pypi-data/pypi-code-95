#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
from typing import Optional

from aibuilder.models.aib_binding import AIBDataType
from aibuilder.models.helpers.exceptions import DataSpecException


class DataSpecification:
    @staticmethod
    def create_data_specification(inputs: dict, outputs: dict) -> str:
        """
        Converts Open API attributes to AI Builder data specification

        :param inputs: Open API Input attributes
        :param outputs: Open API output attributes
        :return: Returns AI Builder data specification
        """
        try:
            input_attributes = DataSpecification.generate_data_spec(inputs)
            output_attributes = DataSpecification.generate_data_spec(outputs, default_data_type="String")
            data_specification = {
                "schemaVersion": 2,
                "input": {"attributes": input_attributes},
                "output": {"attributes": output_attributes}
            }
            return json.dumps(data_specification)
        except Exception as e:
            raise DataSpecException(f"Error occurred when creating AI Builder data specification: {e}")

    @staticmethod
    def generate_data_spec(data: dict, default_data_type: Optional[str] = None) -> list:
        """
        Converts Open API data attribute to AI Builder data attribute type

        :param data: Open API data attributes list
        :param default_data_type: Default AI Builder data type to be used if not supported open data type is found
        :return: Data Attribute specification
        """
        data_attributes = []
        for name, open_api_data_type in data.items():
            if name.lower().endswith("image"):
                aib_data_type = "Image"
            else:
                aib_data_type = DataSpecification.get_spec_data_type(open_api_data_type,
                                                                     default_data_type=default_data_type)
            data_attr = {"specificationName": name, "displayName": name,
                         "requiredLevel": "Recommended", "dataType": aib_data_type}
            data_attributes.append(data_attr)

        return data_attributes

    @staticmethod
    def get_column_types(data: dict, default_data_type: Optional[str] = None) -> dict:
        """
        Returns a dictionary with column names as key and AIB Data type as Value

        :param data: Open API data attributes list
        :param default_data_type: Default AI Builder data type to be used if not supported open data type is found
        :return: Column types dictionary
        """
        column_types = {}
        for name, open_api_data_type in data.items():
            aib_data_type = DataSpecification.get_spec_data_type(open_api_data_type,
                                                                 default_data_type=default_data_type)
            column_types.update({name: AIBDataType(aib_data_type)})

        return column_types

    @staticmethod
    def get_spec_data_type(open_api_data_type: dict, default_data_type=None) -> str:
        """
        Returns AI Builder data specification equivalent data type for given open API data type

        :param open_api_data_type: Open API data type
        :param default_data_type: Default AI Builder data type to be used if not supported open data type is found
        :return: AI Builder data specification data type
        """
        if open_api_data_type.get("format") == 'double' or open_api_data_type.get("type") == 'number':
            data_type = "Double"
        elif open_api_data_type.get('format') == 'string' or open_api_data_type.get("type") == 'string' or \
                open_api_data_type.get('type') == 'object':
            data_type = "String"
        elif open_api_data_type.get('type') == 'bool' or open_api_data_type.get("type") == 'boolean':
            data_type = "Boolean"
        elif open_api_data_type.get('format') == 'int64':
            data_type = "Integer"
        elif default_data_type:
            data_type = default_data_type
        else:
            raise ValueError(f"Open API data type not supported:{open_api_data_type.get('format')}")
        return data_type
