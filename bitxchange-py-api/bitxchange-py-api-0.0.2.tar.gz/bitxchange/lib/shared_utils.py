from typing import Any, Dict, Optional

from bitxchange.errors import ParameterRequiredError, TargetPairError


def remove_none_values(data) -> dict:
    """Remove any `None`-valued items from input dict and return a clean dict."""

    return {key: value for key, value in data.items() if value is not None}


def check_required_parameter(mandatory_params=None, **kwargs):
    """
    Take injected kwargs and validate that there are no empty values.

    If mandatory params are also injected then params will be checked to have
    all mandatory params present before checking for none values.
    """

    # If mandatory params have been passed check mand_params are in params
    if mandatory_params:
        missing_params = []
        for param in mandatory_params:

            if param not in kwargs:
                missing_params.append(param)

        if missing_params:
            raise ValueError(
                f"Following fields are missing as attributes: {','.join(missing_params)}"
            )

    # validate all params have no None values
    for key, value in kwargs.items():
        if not value:
            raise ParameterRequiredError([key])


def validate_target_pair(
    target_pair: str, available_pairs: Optional[Dict[str, Any]] = None
):
    """Takes target_pair and validates they are active pair on the exchange"""

    if not available_pairs:
        from bitxchange.spot import Spot

        spot = Spot()
        available_pairs = spot.available_trading_pairs()

    if target_pair not in available_pairs["combinations"]:
        raise TargetPairError(target_pair) from None

    return str(target_pair)
