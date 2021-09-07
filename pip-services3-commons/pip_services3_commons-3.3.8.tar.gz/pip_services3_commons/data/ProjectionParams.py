# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.ProjectionParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data projection parameters implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Sequence, Any

from pip_services3_commons.data import AnyValueArray


class ProjectionParams(list):
    """
    Defines projection parameters with list if fields to include into query results.

    The parameters support two formats: dot format and nested format.

    The dot format is the standard way to define included fields and subfields using
    dot object notation: **"field1,field2.field21,field2.field22.field221"**.

    As alternative the nested format offers a more compact representation:
    **"field1,field2(field21,field22(field221))"**.

    Example:

    .. code-block:: python
    
         filter = FilterParams.fromTuples("type", "Type1")
         paging = PagingParams(0, 100)
         projection = ProjectionParams.from_value(["field1","field2(field21,field22)"])
            or projection = ProjectionParams.from_string("field1,field2(field21,field22)")

         myDataClient.get_data_by_filter(filter, paging, projection)
    """
    default_delimiter = ','

    def __init__(self, values: Sequence[Any] = None):
        """
        Creates a new instance of the projection parameters and assigns its args.

        :param values: (optional) values to initialize this object.
        """
        super(ProjectionParams, self).__init__()

        if values is not None:
            for value in values:
                self.append("" + value)

    def to_string(self) -> str:
        """
        Gets a string representation of the object.
        The result is a comma-separated list of projection fields
        **"field1,field2.field21,field2.field22.field221"**

        :return: a string representation of the object.
        """
        builder = ''
        index = 0

        while index < len(self):
            if index > 0:
                builder += ','
            builder += self[index]
            index += 1
        return builder

    @staticmethod
    def _parse_value(prefix: str, result: 'ProjectionParams', value: str):
        value = value.strip()
        try:
            if value[0:2] == ' ,':
                value = value[2:]
            elif value[0:2] == ', ':
                value = value[2:]
            elif value[0:1] == ',':
                value = value[1:]
        except KeyError:
            pass
        open_bracket = 0
        open_bracket_index = -1
        close_bracket_index = -1
        comma_index = -1

        break_cycle_required = False
        for index in range(len(value)):
            if value[index] == '(':
                if open_bracket == 0:
                    open_bracket_index = index
                open_bracket += 1

            elif value[index] == ')':
                open_bracket -= 1

                if open_bracket == 0:
                    close_bracket_index = index

                    if open_bracket_index >= 0 and close_bracket_index > 0:
                        previous_prefix = prefix

                        if prefix and len(prefix) > 0:
                            prefix = prefix + '.' + value[0: open_bracket_index]
                        else:
                            prefix = value[0:open_bracket_index]

                        sub_value = value[open_bracket_index + 1: close_bracket_index]
                        ProjectionParams._parse_value(prefix, result, sub_value)

                        sub_value = value[close_bracket_index + 1:]
                        ProjectionParams._parse_value(previous_prefix, result, sub_value)
                        break_cycle_required = True

            elif value[index] == ',':
                if open_bracket == 0:
                    comma_index = index
                    sub_value = value[0:comma_index]

                    if sub_value and len(sub_value) > 0:
                        if prefix and len(prefix) > 0:
                            result.append(prefix + '.' + sub_value)
                        else:
                            result.append(sub_value)

                        sub_value = value[comma_index + 1:]

                        if sub_value and len(sub_value) > 0:
                            ProjectionParams._parse_value(prefix, result, sub_value)
                            break_cycle_required = True

            if break_cycle_required:
                break

        if value and len(value) > 0 and open_bracket_index == -1 and comma_index == -1:
            if prefix and len(prefix) > 0:
                result.append(prefix + '.' + value)
            else:
                result.append(value)

    @staticmethod
    def from_value(value: Any) -> 'ProjectionParams':
        """
          Converts specified args into ProjectionParams.

          :param value: args to be converted

          :return: a newly created ProjectionParams.
          """
        value = AnyValueArray.from_value(value)
        return ProjectionParams(value)

    @staticmethod
    def from_string(*values: str) -> 'ProjectionParams':
        """
        Parses comma-separated list of projection fields.

        :param values: one or more comma-separated lists of projection fields
        :return: a newly created ProjectionParams.
        """
        result = ProjectionParams()
        values = list(values)
        for value in values:
            ProjectionParams._parse_value('', result, value)

        return result
