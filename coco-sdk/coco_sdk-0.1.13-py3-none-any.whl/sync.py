import os
import uuid

import requests

from .coco import CoCoResponse, ConversationalComponentBase, ComponentSessionBase

COCOHUB_URL = os.environ.get("COCOHUB_URL", "https://cocohub.ai")


def exchange(
    component_id: str, session_id: str, user_input: str = None, **kwargs
) -> CoCoResponse:
    """
    A thin wrapper to call the coco exchange endpoint.
    Similar to the endpoint, component_id, and session_id are mandatory
    everything else is optional.

    Optional paramters:
        user_input - a user input string
        context - dict with keys specified according to the context transfer spec:
        https://docs.cocohub.ai/

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
    coco_resp = requests.post(
        f"{COCOHUB_URL}/api/exchange/{component_id}/{session_id}",
        json=payload,
    ).json()
    return CoCoResponse(**coco_resp, raw_resp=coco_resp)


def generate_session_id():
    return str(uuid.uuid4())


class ConversationalComponent(ConversationalComponentBase):
    """
    A component class to hold a reference to a single component.

    initalize it with a component id.
    then call it with session_id and more optional parameters.
    """

    def __call__(
        self, session_id: str, user_input: str = None, **kwargs
    ) -> CoCoResponse:
        return exchange(self.component_id, session_id, user_input, **kwargs)


class ComponentSession(ComponentSessionBase):
    """
    This class can manage both component and session.

    Initialize it with component_id, and session_id
    """

    def __init__(self, component_id: str, session_id: str = None):
        super().__init__(component_id, session_id=session_id)
        self.component = ConversationalComponent(component_id)

    def __call__(self, user_input: str = None, **kwargs) -> CoCoResponse:
        """
        Can be called with any parameters

        Should be used mostly with user_input and context
        """
        return self.component(self.session_id, user_input, **kwargs)
