"""
Exceptions.
"""


# ============================================================================
# =========================== Parsing stage exceptions =======================
# ============================================================================

class ParseStructureError(TypeError):
    """
    The base type for exceptions at parsing stage.
    """

    pass


class ParseMismatchLength(ParseStructureError):
    """
    Mismatching between expected and received data lengths
    """

    def __init__(self, field_name: str, received: int, expected: int):
        """Get error info and forward formatted message to super"""
        message = f'Length of {field_name} should be: {expected}; ' \
                  f'received: {received}.'
        super().__init__(message)


# ============================================================================
# =========================== Decoding stage exceptions ======================
# ============================================================================


class ABIGettingError(IOError):
    """
    The base type for exceptions ot ABI getting.
    """

    pass


class ABIEtherscanNetworkError(ABIGettingError):
    """
    Exception while calling Etherscan API.
    """

    pass


class ABIEtherscanStatusCode(ABIGettingError):
    """
    Etherscan API return failure status code.
    """

    def __init__(self, status_code: str, message: str, result: str):
        """Get error info and forward formatted message to super"""
        msg = f'Code: {status_code}. ' \
              f'Message: {message}. ' \
              f'Result: {result}.'
        super().__init__(msg)


class ABILocalFileNotExisted(ABIGettingError):
    """
    File with ABI specification does not exist.
    """

    def __init__(self, target_file: str):
        """Prepare and forward error message."""
        msg = f'File of interface does not exist: {target_file}.'
        super().__init__(msg)
