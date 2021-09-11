"""
description: this module provides exceptions which may appear in pistar echo agent.
"""


class ServerMissingArgumentSchemaException(Exception):
    """
    description: if the schema of argument does not exist,
                 raise this exception.
    """

    def __init__(self, application_name, argument_name):
        super().__init__(
            'cannot find the schema of argument \'{argument_name}\' '
            'in application \'{application_name}\''.format(
                argument_name=argument_name,
                application_name=application_name
            )
        )


class ServerMissingArgumentSchemaFieldException(Exception):
    """
    description: if an argument field does not exist, raise this exception.
    """

    def __init__(self, field_name, application_name, argument_name):
        super().__init__(
            (
                'cannot find field \'{field_name}\' in schema of ' +
                'argument \'{argument_name}\' in application \''
                '{application_name}\'').format(
                    field_name=field_name,
                    argument_name=argument_name,
                    application_name=application_name
            )
        )


class ServerMissingDocumentFieldException(Exception):
    """
    description: if these is no __doc__ in an application,
                 raise this exception.
    """

    def __init__(self, application_name, field_name):
        super().__init__(
            'cannot find the field \'{field_name}\' in application'
            ' \'{application_name}\''.format(
                field_name=field_name,
                application_name=application_name
            )
        )


class ServerUnknownArgumentSchemaException(Exception):
    """
    description: if there is an unknown argument in the arguments schema,
                 raise this exception.
    """

    def __init__(self, application_name, schema_name):
        super().__init__(
            'unknown schema \'{schema_name}\' in application'
            ' \'{application_name}\''.format(
                application_name=application_name,
                schema_name=schema_name
            )
        )


class ServerUnknownArgumentSourceException(Exception):
    """
    description: if the argument source is invalid, raise this exception.
    """

    def __init__(self, application_name, source, argument_name):
        super().__init__(
            'unknown source \'from {source}\' of argument \'{argument_name}\''
            ' in application \'{application_name}\''.format(
                application_name=application_name,
                argument_name=argument_name,
                source=source
            )
        )


class ServerMissingArgumentInRequestException(Exception):
    """
    description: if the request does not contain the argument,
                 raise this exception.
    """

    def __init__(self, application_name, source, argument_name):
        super().__init__(
            (
                'cannot find argument \'{argument_name}\' in \'{source}\' of '
                + 'request in application_name \'{application_name}\''
            ).format(
                application_name=application_name,
                argument_name=argument_name,
                source=source
            )
        )


class ServerRequestBodyFormatException(Exception):
    """
    description: if the format of request body is invalid,
                 raise this exception.
    """

    def __init__(self, application_name, detail):
        super().__init__(
            'the request body of application \'{application_name}\' '
            'must be in json format, the detail is {detail}'.format(
                application_name=application_name, detail=detail
            )
        )
