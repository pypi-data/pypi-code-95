class LlcAPIClientError(Exception):
    pass


class ApiGeneralError(LlcAPIClientError):
    def __init__(self, error_message, message="There was an error with the API."):
        self.error_message = error_message
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f" {self.message} -> {self.error_message}"


class ApiTokenError(LlcAPIClientError):
    def __init__(self, message="There is no valid auth token available. Please login using ScienceSdk.login(username, "
                               "password)"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f" {self.message}"


class ApiAuthenticationError(LlcAPIClientError):
    def __init__(
            self, error_message, message="There was an error with authentication."
    ):
        self.error_message = error_message
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f" {self.message} -> {self.error_message}"
