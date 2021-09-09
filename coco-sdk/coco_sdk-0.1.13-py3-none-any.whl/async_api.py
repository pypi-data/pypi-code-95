import os
from typing import List
import uuid

from httpx import AsyncClient

from .coco import (
    CoCoResponse,
    ConversationalComponentBase,
    ComponentSessionBase,
    CoCoIntentResult,
)

COCOHUB_URL = os.environ.get("COCOHUB_URL", "https://cocohub.ai")


async def query_intents(
    intent_names: List[str], query: str = ""
) -> List[CoCoIntentResult]:
    """
    A thin wrapper to call the coco query intents endpoint.

    Arguments:
        intent_names: (List[str]) List of strings when each string is an existing and valid intent name.
        query: (string) The query that will be examined by each intent.

    Response:
        List of CoCo intent responses.
    """
    payload = {"query": query, "intent_names": intent_names}

    async with AsyncClient() as http_client:
        http_resp = await http_client.post(
            f"{COCOHUB_URL}/v2/intent/query",
            json=payload,
        )
    coco_resp = http_resp.json()
    return [CoCoIntentResult(**r) for r in coco_resp]


async def exchange(
    component_id: str, session_id: str, user_input: str = None, **kwargs
) -> CoCoResponse:
    """
    A thin wrapper to call the coco exchange endpoint.
    Similar to the endpoint, component_id, and session_id are mandatory
    everything else is optional.

    Optional paramters:
        user_input - a user input string
        context - dict with keys specified according to the context transfer spec:
        https://docs.cocohub.ai

    Arguments:
        component_id {str} -- A CoCo component id from the marketplace gateway
                              (published at cocohub.ai)
        session_id {str} -- a randomly generated session id to identify the session(conversation)

    Returns:
        CoCoResponse instance
    """
    payload = kwargs
    if user_input:
        payload = {"user_input": user_input, **kwargs}
    async with AsyncClient() as http_client:
        http_resp = await http_client.post(
            f"{COCOHUB_URL}/api/exchange/{component_id}/{session_id}",
            json=payload,
        )
    coco_resp: dict = http_resp.json()
    return CoCoResponse(**coco_resp, raw_resp=coco_resp)


def generate_session_id():
    return str(uuid.uuid4())


class ConversationalComponent(ConversationalComponentBase):
    """
    A component class to hold a reference to a single component.

    initalize it with a component id.
    then call it with session_id and more optional parameters.
    """

    async def __call__(
        self, session_id: str, user_input: str = None, **kwargs
    ) -> CoCoResponse:
        return await exchange(self.component_id, session_id, user_input, **kwargs)


class ComponentSession(ComponentSessionBase):
    """
    This class can manage both component and session.

    Initialize it with component_id, and session_id
    """

    def __init__(self, component_id: str, session_id: str = None):
        super().__init__(component_id, session_id=session_id)
        self.component = ConversationalComponent(component_id)

    async def __call__(self, user_input: str = None, **kwargs) -> CoCoResponse:
        """
        Can be called with any parameters

        Should be used mostly with user_input and context
        """
        return await self.component(self.session_id, user_input, **kwargs)
