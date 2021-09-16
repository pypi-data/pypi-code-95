import json

from openapi_client.exceptions import ApiException

DEFAULT_ERROR_MESSAGE = "An unexpected exception occurred. Use SAVVIHUB_LOG=DEBUG to view stack trace. (`pip install --upgrade savvihub` might resolve this issue.)"


class SavvihubException(Exception):
    def __init__(self, message=DEFAULT_ERROR_MESSAGE, exit_code=1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)


class SavvihubApiException(SavvihubException):
    @classmethod
    def convert_api_exception(
        cls, api_exception: ApiException
    ) -> "SavvihubApiException":
        try:
            body = json.loads(api_exception.body)
        except json.JSONDecodeError:
            return cls()

        body_code = body.get("code")
        body_message = body.get("message", "")
        message = (
            f"{body_code} ({api_exception.status})"
            f"{': ' + body_message if body_message else ''}"
        )

        fields = body.get("fields")
        if fields:
            additional_messages = []
            for field in fields:
                field_name = field.get("name", "")
                field_value = field.get("value", "")
                field_message = field.get("message")
                additional_messages.append(
                    f"{field_name}: {field_value}"
                    f"{'(' + field_message + ')' if field_message else ''}"
                )
            message += f" {', '.join(additional_messages)}."

        return cls(message=message)


class GitError(SavvihubException):
    pass


class TimeoutError(SavvihubException):
    pass


class InvalidDatasetError(SavvihubException):
    pass


class InvalidKernelImageError(SavvihubException):
    pass


class InvalidKernelResourceSpecError(SavvihubException):
    pass


class InvalidOrganizationError(SavvihubException):
    pass


class InvalidExperimentError(SavvihubException):
    pass


class InvalidProjectError(SavvihubException):
    pass


class InvalidTokenError(SavvihubException):
    pass


class InvalidVolumeFileError(SavvihubException):
    pass


class InvalidVolumeMountError(SavvihubException):
    pass


class InvalidWorkspaceError(SavvihubException):
    pass


class InvalidParamsError(SavvihubException):
    pass
