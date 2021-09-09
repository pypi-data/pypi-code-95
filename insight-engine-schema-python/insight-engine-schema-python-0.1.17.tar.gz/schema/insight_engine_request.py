# -*- coding: utf-8 -*-
import typing

from typing import List
from pydantic import Field, root_validator
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic.errors import MissingError, NoneIsNotAllowedError

from fhir.resources import backboneelement, domainresource, fhirtypes

from fhir.resources.claim import Claim


class HistoryClaim(domainresource.DomainResource):
    """ HistoryClaim contains additional information apart from just the claim.
    """

    resource_type = Field("HistoryClaim", const=True)

    claim: Claim = Field(
        None,
        alias="claim",
        title="Old Claim",
        description="Claim itself as it was supplied",
        element_property=True,
    )

    transaction_id: str = Field(
        None,
        alias="transactionId",
        title="Old transaction identifier",
        description="ID of transaction when we received the claim",
        element_property=True,
    )

    client_id: str = Field(
        None,
        alias="clientId",
        title="client identifier",
        element_property=True,
    )

    member_id: str = Field(
        None,
        alias="memberId",
        title="member identifier",
        element_property=True,
    )

    created_at: str = Field(
        None,
        alias="createdAt",
        title="createdAt",
        element_property=True,
    )

    context: str = Field(
        None,
        alias="context",
        title="context",
        element_property=True,
    )


class InsightEngineRequest(domainresource.DomainResource):
    """ Insight Engine request.

    Request contains the original claim, history of the patient and 
    additional reference data that is required by the insight engine.
    """

    resource_type = Field("InsightEngineRequest", const=True)

    claim: Claim = Field(
        None,
        alias="claim",
        title="Claim Under Evaluation (CUE)",
        description=(
            "Claim that this policy should evaluate"
        ),
        # if property is element of this resource.
        element_property=True,
    )
    history: List[HistoryClaim] = Field([], alias="history", element_property=True)
    referenceData: List[str] = Field([])

    transaction_id: str = Field(
        None,
        alias="transactionId",
        title="Transaction identifier",
        description=(
            "This is part of clients' request. Is needed to correlate the incoming request "
            "and subsequent response"
        ),
        # if property is element of this resource.
        element_property=True,
    )

