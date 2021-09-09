import uuid
import json

from pygments import highlight, lexers, formatters


class CoCoIntentResult:
    def __init__(self, confidence: float, result: bool, name: str = None, **kwargs):
        self.name = name
        self.confidence = confidence
        self.result = result

        for k, karg in kwargs.items():
            setattr(self, k, karg)


class CoCoResponse:
    def __init__(
        self,
        response: str = "",
        component_done: bool = False,
        component_failed: bool = False,
        updated_context: dict = {},
        confidence: float = 1.0,
        out_of_context: bool = False,
        outputs: dict = {},
        raw_resp: dict = {},
        **kwargs
    ):
        self.response: str = response
        self.component_done: bool = component_done
        self.component_failed: bool = component_failed
        self.updated_context: dict = updated_context
        self.confidence: float = confidence
        self.out_of_context: bool = out_of_context
        self.raw_resp: dict = raw_resp
        self.outputs = outputs

        for k, karg in kwargs.items():
            setattr(self, k, karg)

    def __repr__(self):
        instance_dict = {k: v for k, v in self.__dict__.items() if k != "raw_resp"}
        formatted_json = json.dumps(instance_dict, indent=True)
        colorful_json = highlight(
            formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
        )
        return colorful_json


def generate_session_id():
    return str(uuid.uuid4())


class ConversationalComponentBase:
    """
    A component class to hold a reference to a single component.

    initalize it with a component id.
    then call it with session_id and more optional parameters.
    """

    def __init__(self, component_id: str):
        self.component_id = component_id

    def __call__(
        self, session_id: str, user_input: str = None, **kwargs
    ) -> CoCoResponse:
        raise NotImplementedError


class ComponentSessionBase:
    """
    This class can manage both component and session.

    Initialize it with component_id, and session_id
    """

    def __init__(self, component_id: str, session_id: str = None):
        if not session_id:
            self.session_id = generate_session_id()
        else:
            self.session_id = session_id

    def __call__(self, user_input: str = None, **kwargs) -> CoCoResponse:
        """
        Can be called with any parameters

        Should be used mostly with user_input and context
        """
        raise NotImplementedError
