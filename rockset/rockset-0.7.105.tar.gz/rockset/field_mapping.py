"""
Introduction
------------

FieldMapping objects allow you to specify transformations to be applied on all documents inserted
into a collection. Any valid SQL can be applied on any field in a document.

For more information on field mappings, refer to `the official documentation <https://rockset.com/docs/field-mappings/>`_.

Example of basic field mapping
------------------------------
::

    from rockset import Client

    rs = Client()

    mappings = [
        rs.FieldMapping.mapping(
            name="anonymize_name",
            input_fields=[
                rs.FieldMapping.input_field(
                    field_name="name",
                    if_missing="SKIP",
                    is_drop=True,
                    param="name"
                )
            ],
            output_field=rs.FieldMapping.output_field(
                field_name="name", sql_expression="SHA256(:name)", on_error="FAIL"
            )
        )
    ]

    # This collection will have all its `name` fields anonymized through the SQL expression
    # in the output field above.
    collection = rs.Collection.create(name="collection", field_mappings=mappings)

Example of field whitelisting
-----------------------------
::

    from rockset import Client

    rs = Client()

    mappings = [
        rs.FieldMapping.mapping(name="drop_all_fields", is_drop_all_fields=True),
        rs.FieldMapping.mapping(
            name="whitelist_name",
            input_fields=[
                rs.FieldMapping.input_field(
                    field_name="name",
                    if_missing="SKIP",
                    is_drop=True,
                    param="name"
                )
            ],
            output_field=rs.FieldMapping.output_field(
                field_name="name", sql_expression=":name", on_error="FAIL"
            )
        )
    ]

    # This collection will have `name` as a whitelisted field, essentially dropping all fields
    # except for `name`.
    collection = rs.Collection.create(name="collection", field_mappings=mappings)

"""


class FieldMapping(object):
    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)

    @classmethod
    def mapping(
        cls,
        name,
        is_drop_all_fields=None,
        input_fields=None,
        output_field=None
    ):
        """Creates a new mapping object

        Args:
            name(str): Name of the mapping
            is_drop_all_fields(bool): Whether to drop all the fields in a document. This can only be set once
                in a list of field mappings, and a mapping specifying `is_drop_all_fields` cannot have any input or output fields
            input_fields: An Array of InputField objects
            output: An OutputField object
        """
        input_dict = [dict(f) for f in input_fields] if input_fields else None
        output_dict = dict(output_field) if output_field else None

        return Mapping(
            name=name,
            is_drop_all_fields=is_drop_all_fields,
            input_fields=input_dict,
            output_field=output_dict
        )

    @classmethod
    def input_field(cls, field_name, param=None, if_missing=None, is_drop=None):
        """Create a new InputField object

        Args:
            field_name (str): The name of the field, parsed as a SQL qualified name
            param (str): SQL parameter name (default: same as field name. Required
                if the field name is nested)

                if_missing (str): Define the behavior if the field is missing from the document or is NULL,
                one of:

                    * `SKIP`: skip the SQL expression in the output field, i.e. acts as if the field mapping does not exist

                    * `PASS`: pass NULL to the SQL expression specified in the output field

                Default is `SKIP`.
            is_drop (boolean): Set to true if the input field needs to be dropped
        """
        return InputField(
            field_name=field_name,
            param=param,
            if_missing=if_missing,
            is_drop=is_drop
        )

    @classmethod
    def output_field(cls, field_name, sql_expression, on_error=None):
        """Create a new OutputField object

        Args:
            field_name (str): The name of the field, parsed as SQL qualified name
            value (Value): SQL expression
            on_error (str): Define the behavior if the SQL expression fails, one of:

                * `SKIP`: skip the SQL expression, i.e. acts as if the mapping does not exist

                * `FAIL`: fail the entire mapping, i.e. acts as if the document does not exist

                Default is `SKIP`.
        """
        return OutputField(
            field_name=field_name,
            sql_expression=sql_expression,
            on_error=on_error
        )


class Mapping(FieldMapping):
    def __init__(
        self,
        name,
        is_drop_all_fields=None,
        input_fields=None,
        output_field=None
    ):
        self.name = name
        self.is_drop_all_fields = is_drop_all_fields
        self.input_fields = input_fields

        if output_field is not None:
            self.output_field = output_field


class InputField:
    def __init__(self, field_name, param=None, if_missing=None, is_drop=None):
        self.field_name = field_name
        if param is not None:
            self.param = param
        if if_missing is not None:
            self.if_missing = if_missing
        if is_drop is not None:
            self.is_drop = is_drop
        return

    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)


class OutputField:
    def __init__(self, field_name, sql_expression, on_error=None):
        self.field_name = field_name
        self.value = {
            'sql': sql_expression,
        }
        if on_error is not None:
            self.on_error = on_error
        return

    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)
