class ForecastFlowError(Exception):
    """
    Base Exception of ForecastFlow
    """


class InvalidID(ForecastFlowError):
    """
    ID is not found or invalid.
    """


class OperationFailed(ForecastFlowError):
    """
    Data Source, Model or Prediction quit with Error.
    """
