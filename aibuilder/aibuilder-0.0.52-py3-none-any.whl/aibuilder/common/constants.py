#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------


from enum import Enum


class OpenAPIConstants(Enum):
    """
    Open API constants

    """
    filter = "$filter"
    equals = "eq"
    value = "value"
    object_id = "id"


class GraphClientConstants(Enum):
    """
    Graph client constants

    """
    graph_api_version = "v1.0"
    service_principal_path = "servicePrincipals"
    application_id_key = "appId"
    # application_id = "c66c5581-84bd-47bf-aabd-89a02c13b85c"
    # tip app id
    # application_id = "0527d918-8aec-4c44-9f4e-86cc8b88d87b"
    # prod app id
    application_id = "be5f0473-6b57-40f8-b0a9-b3054b41b99e"
