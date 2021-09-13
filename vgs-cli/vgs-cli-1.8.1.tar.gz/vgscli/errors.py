import traceback
from functools import wraps

import click
from click import UsageError, Context
from click.exceptions import Abort, Exit
from simple_rest_client import exceptions


class VgsCliError(UsageError):
    def __init__(self, message, ctx=None):
        self.message = message
        self.ctx = ctx

    def show(self, file=None):
        self.show_message()

    def show_message(self):
        if self.ctx and self.ctx.obj.debug:
            click.echo(traceback.format_exc(), err=True)
        click.echo(self.message, err=True)


class VaultNotFoundError(VgsCliError):
    def __init__(self, vault_id, ctx=None):
        self.message = "Vault " + vault_id + " doesn't exist."
        self.ctx = ctx


class TokenNotValidError(VgsCliError):
    def __init__(self, ctx=None):
        self.message = 'Please run `vgs login` because your session has been expired.'
        self.ctx = ctx


class AuthenticationRequiredError(VgsCliError):
    def __init__(self, ctx=None):
        self.message = 'Please run `vgs login` because your session has been expired.'
        self.ctx = ctx


class AuthenticationError(VgsCliError):
    def __init__(self, ctx=None, details=None):
        self.message = 'Authentication error occurred' if ctx and ctx.obj.debug \
            else 'Authentication error occurred.'

        if details:
            self.message = '{message} {details}'.format(
                message=self.message,
                details=details
            )

        self.ctx = ctx


class ClientCredentialsAuthenticationError(VgsCliError):
    def __init__(self, ctx=None):
        self.message = """Authentication error occurred.
                    
NOTE: You may see this error if you're using an account with enabled OTP. 
Auto login via environment variables with OTP is not supported. 
 """ if ctx and ctx.obj.debug \
            else """Authentication error occurred. (Run with --debug for a traceback.)
                    
NOTE: You may see this error if you're using an account with enabled OTP. 
Auto login via environment variables with OTP is not supported. 
 """
        self.ctx = ctx


class ApiError(VgsCliError):
    def __init__(self, e, ctx=None):
        self.message = 'API error occurred.' if ctx and ctx.obj.debug \
            else 'API error occurred. (Run with --debug for a traceback.)'
        self.ctx = ctx


class UnhandledError(VgsCliError):
    def __init__(self, ctx=None):
        self.message = 'An unexpected error occurred.' if ctx and ctx.obj.debug \
            else 'An unexpected error occurred. (Run with --debug for a traceback.)'
        self.ctx = ctx


class RouteNotValidError(VgsCliError):

    def __init__(self, error_message: str, ctx=None):
        error_message = f'Route cannot be applied due to errors:\n{error_message}'
        self.message = error_message if ctx and ctx.obj.debug \
            else f'{error_message} (Run with --debug for a traceback.)'
        self.ctx = ctx


class SchemaValidationError(VgsCliError):
    def __init__(self, message, ctx=None):
        self.message = f'Error during validation of the file input: {message}.'
        self.ctx = ctx


class ServiceClientCreationError(VgsCliError):
    def __init__(self, e, ctx=None):
        details = [x["detail"] for x in e.response.body['errors']]
        self.message = f"Service Account creation failed with error: {details}"
        self.ctx = ctx


class ServiceClientDeletionError(VgsCliError):
    def __init__(self, e, ctx=None):
        details = [x["detail"] for x in e.response.body['errors']]
        self.message = f"Service Account deletion failed with error: {details}"
        self.ctx = ctx


class NoSuchFileOrDirectoryError(VgsCliError):
    def __init__(self, message, ctx=None):
        self.message = f'No such file or directory: {message}'
        self.ctx = ctx


class InsufficientPermissionsError(VgsCliError):
    def __init__(self, ctx=None):
        self.message = "You don't have enough permissions to perform this operation. Please contact support@verygoodsecurity.com."
        self.ctx = ctx


class PermissionDeniedError(VgsCliError):
    def __init__(self, ctx=None):
        self.message = "You don't have enough permissions to the requested resource"
        self.ctx = ctx


def handle_errors(**outer_kwargs):
    def decorator_handle_errors(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (Abort, Exit):
                raise
            except exceptions.ClientError as e:
                if args[0] and isinstance(args[0], Context):
                    if e.response.status_code == 403:
                        if e.response.body:
                            raise outer_kwargs.get('InsufficientPermissionsError', InsufficientPermissionsError)(ctx=args[0])
                        raise outer_kwargs.get('PermissionDeniedError', PermissionDeniedError)(ctx=args[0])
                    raise outer_kwargs.get('ApiError', ApiError)(e, ctx=args[0])
            except VgsCliError:
                raise
            except Exception:
                if args[0] and isinstance(args[0], Context):
                    raise UnhandledError(ctx=args[0])

        return wrapper
    return decorator_handle_errors
