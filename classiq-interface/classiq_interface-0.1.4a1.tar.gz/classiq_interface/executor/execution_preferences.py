from typing import Optional, Union, List

import pydantic

from classiq_interface.backend.backend_preferences import (
    AzureBackendPreferences,
    IBMBackendPreferences,
    AwsBackendPreferences,
    IonqBackendPreferences,
)


class AmplitudeEstimation(pydantic.BaseModel):
    alpha: float = pydantic.Field(
        default=0.05, description="Confidence level of the AE algorithm"
    )
    epsilon: float = pydantic.Field(
        default=0.01, description="precision for estimation target `a`"
    )
    binary_search_threshold: Optional[pydantic.confloat(ge=0, le=1)] = pydantic.Field(
        description="The required probability on the tail of the distribution (1 - percentile)"
    )


class AmplitudeAmplification(pydantic.BaseModel):
    iterations: Union[List[int], int, None] = pydantic.Field(
        default=None, description="Number or list of numbers of iteration to use"
    )
    growth_rate: Optional[float] = pydantic.Field(
        default=None,
        description="Number of iteration used is set to round(growth_rate**iterations)",
    )
    sample_from_iterations: bool = pydantic.Field(
        default=False,
        description="If True, number of iterations used is picked randomly from [1, iteration] range",
    )


class ExecutionPreferences(pydantic.BaseModel):
    num_shots: int = 100
    timeout_sec: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        description="If set, limits the execution runtime. Value is in seconds. Not supported on all platforms.",
    )
    amplitude_estimation: Optional[AmplitudeEstimation] = pydantic.Field(
        default_factory=AmplitudeEstimation
    )
    amplitude_amplification: Optional[AmplitudeAmplification] = pydantic.Field(
        default_factory=AmplitudeAmplification
    )
    backend_preferences: Union[
        AzureBackendPreferences,
        IBMBackendPreferences,
        AwsBackendPreferences,
        IonqBackendPreferences,
    ] = pydantic.Field(
        default_factory=lambda: IBMBackendPreferences(
            backend_service_provider="IBMQ", backend_name="aer_simulator_statevector"
        ),
        description="Preferences for the requested backend to run the quantum circuit.",
    )
