from typing import Literal

import pydantic

from classiq_interface.backend.quantum_backend_providers import (
    ProviderVendor,
    BACKEND_PROVIDERS_DICT,
    IonqBackendNames,
)


class BackendPreferences(pydantic.BaseModel):
    backend_service_provider: str = pydantic.Field(
        description="Provider company for the requested backend."
    )
    backend_name: str = pydantic.Field(description="Name of the requested backend.")


class AwsBackendPreferences(BackendPreferences):
    _BACKEND_SERVICE_PROVIDER = ProviderVendor.AWS_BRAKET
    backend_service_provider: Literal[_BACKEND_SERVICE_PROVIDER.value]
    backend_name: Literal[
        tuple(name.value for name in BACKEND_PROVIDERS_DICT[_BACKEND_SERVICE_PROVIDER])
    ]
    aws_access_key_id: pydantic.constr(
        strip_whitespace=True,
        min_length=20,
        max_length=20,
        regex="(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])",
    ) = pydantic.Field(description="AWS Access Key ID")
    aws_secret_access_key: pydantic.constr(
        strip_whitespace=True,
        min_length=40,
        max_length=40,
        regex="(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])",
    ) = pydantic.Field(description="AWS Secret Access Key")
    region_name: pydantic.constr(strip_whitespace=True, min_length=1) = pydantic.Field(
        description="AWS Region name"
    )
    s3_bucket_name: pydantic.constr(
        strip_whitespace=True, min_length=3
    ) = pydantic.Field(description="S3 Bucket Name")
    s3_bucket_key: pydantic.constr(
        strip_whitespace=True, min_length=1
    ) = pydantic.Field(description="S3 Bucket Key")


class IBMBackendPreferences(BackendPreferences):
    _BACKEND_SERVICE_PROVIDER = ProviderVendor.IBMQ
    backend_service_provider: Literal[
        _BACKEND_SERVICE_PROVIDER.value
    ] = _BACKEND_SERVICE_PROVIDER
    backend_name: Literal[
        tuple(name.value for name in BACKEND_PROVIDERS_DICT[_BACKEND_SERVICE_PROVIDER])
    ]


class AzureBackendPreferences(BackendPreferences):
    _BACKEND_SERVICE_PROVIDER = ProviderVendor.AZURE_QUANTUM
    backend_service_provider: Literal[_BACKEND_SERVICE_PROVIDER.value]
    backend_name: Literal[
        tuple(name.value for name in BACKEND_PROVIDERS_DICT[_BACKEND_SERVICE_PROVIDER])
    ]


IONQ_API_KEY_LEGTH: int = 32


class IonqBackendPreferences(BackendPreferences):
    _BACKEND_SERVICE_PROVIDER = ProviderVendor.IONQ
    backend_service_provider: Literal[
        _BACKEND_SERVICE_PROVIDER.value
    ] = _BACKEND_SERVICE_PROVIDER
    backend_name: IonqBackendNames = pydantic.Field(
        default=IonqBackendNames.SIMULATOR,
        description="IonQ backend for quantum programs execution.",
    )
    api_key: pydantic.constr(
        regex=f"[A-Za-z0-9]{{{IONQ_API_KEY_LEGTH}}}"
    ) = pydantic.Field(..., description="IonQ API key")
