from typing import List, Dict, Any, Union


class Interface():
    def __init__(self, **kwargs):
        pass

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)


class Text(Interface):
    def __init__(self, mutations: Union[str, Dict[str, str]]):
        if isinstance(mutations, str):
            self.mutations = {"original": mutations}
        else:
            self.mutations = mutations

    def add_mutation(self, key, mutation):
        self.mutations[key] = mutation

    def get(self, key="original") -> str:
        return self.mutations[key] if key in self.mutations else ""

    def to_dict(self):
        return self.mutations

    def get_keys(self):
        return [k for k in self.mutations]

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["mutations"],
        )


class Entity(Interface):
    def __init__(self, name: str, input_type: str, val: str, sidx: int, eidx: int, confidence: float) -> None:
        self.name = name
        self.input_type = input_type
        self.val = val
        self.sidx = sidx
        self.eidx = eidx
        self.confidence = confidence

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["name"],
            dict["input_type"],
            dict["val"],
            dict["sidx"],
            dict["eidx"],
            dict["confidence"],
        )


class Intent(Interface):
    def __init__(self, chosen: str, scores: Dict[str, float]) -> None:
        self.chosen = chosen
        self.scores = scores

    def is_intent_chosen(self):
        return self.chosen != ""

    def confidence(self):
        return self.scores[self.chosen]

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["chosen"],
            dict["scores"],
        )


class Misc(Interface):
    def __init__(self,
                 buttons: List[str] = None,
                 multiselects: List[str] = None,
                 checkboxes: List[str] = None,
                 date: str = None,
                 file: str = None,
                 latitude: str = None,
                 longitude: str = None,
                 nfc: Any = None,
                 form: Dict[str, Any] = None
                 ):
        self.buttons = buttons
        self.multiselects = multiselects
        self.checkboxes = checkboxes
        self.date = date
        self.file = file
        self.latitude = latitude
        self.longitude = longitude
        self.nfc = nfc
        self.form = form

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["buttons"] if "buttons" in dict else None,
            dict["multiselects"] if "multiselects" in dict else None,
            dict["checkboxes"] if "checkboxes" in dict else None,
            dict["date"] if "date" in dict else None,
            dict["file"] if "file" in dict else None,
            dict["latitude"] if "latitude" in dict else None,
            dict["longitude"] if "longitude" in dict else None,
            dict["nfc"] if "nfc" in dict else None,
            dict["form"] if "form" in dict else None,
        )


class UserMessage(Interface):
    def __init__(self,
                 user_id: str = None,
                 text: Text = None,
                 misc: Misc = None,
                 intent: Intent = None,
                 entities: List[Entity] = None):
        self.user_id = user_id
        self.text = text
        self.misc = misc
        self.intent = intent
        self.entities = entities

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "text": self.text.to_dict() if self.text is not None else None,
            "misc": self.misc.to_dict() if self.misc is not None else None,
            "intent": self.intent.to_dict() if self.intent is not None else None,
            "entities": [e.to_dict() for e in self.entities] if self.entities is not None else None
        }

    def select(self, key):
        args = key.split(":")
        if args[0] == "text":
            return self.text.get(args[1])  # type:ignore
        elif args[0] == "intent":
            return self.intent.chosen  # type:ignore
        elif args[0] == "entity":
            for e in self.entities:  # type:ignore
                if e.name == args[1]:
                    return e.val
        return ""

    def get_entity_val(self, name, default=None):
        if self.entities is not None:
            for e in self.entities:
                if e.name == name:
                    return e.val
        return default

    @classmethod
    def from_dict(cls, message_dict):
        def is_exist(key):
            return key in message_dict and message_dict[key] is not None

        obj = cls()
        obj.user_id = message_dict["user_id"] if is_exist("user_id") else None
        obj.text = Text(message_dict["text"]) if is_exist("text") else None
        obj.misc = Misc.from_dict(message_dict["misc"]) if is_exist("misc") else None
        obj.intent = Intent.from_dict(
            message_dict["intent"]) if is_exist("intent") else None
        obj.entities = [Entity.from_dict(
            e) for e in message_dict["entities"]] if is_exist("entities") else None
        return obj


class ActorMessage(Interface):
    def __init__(self,
                 user_id: str = None,
                 code: str = None,
                 text: str = None,
                 list: List[str] = None,
                 buttons: List[str] = None,
                 checkboxes: List[str] = None,
                 multiselects: List[str] = None,
                 images: List[str] = None,
                 files: List[str] = None,
                 misc: Any = None):
        self.user_id = user_id
        self.code = code
        self.text = text
        self.buttons = buttons
        self.checkboxes = checkboxes
        self.multiselects = multiselects
        self.images = images
        self.files = files
        self.list = list
        self.misc = misc

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["user_id"] if "user_id" in dict else None,
            dict["code"] if "code" in dict else None,
            dict["text"] if "text" in dict else None,
            dict["list"] if "list" in dict else None,
            dict["buttons"] if "buttons" in dict else None,
            dict["checkboxes"] if "checkboxes" in dict else None,
            dict["multiselects"] if "multiselects" in dict else None,
            dict["images"] if "images" in dict else None,
            dict["files"] if "files" in dict else None,
            dict["misc"] if "misc" in dict else None
        )


class Command:
    class Do(Interface):
        def __init__(self, action: str, request: UserMessage) -> None:
            self.name = "do"
            self.action = action
            self.request = request

        def app(self):
            return self.action.split(":")[0]

        def action_name(self):
            return self.action.split(":")[1]

        def to_dict(self):
            return {
                "name": "do",
                "action": self.action,
                "request": self.request.to_dict()
            }

        @classmethod
        def from_dict(cls, dict):
            return cls(dict["action"], UserMessage.from_dict(dict["request"]))

    class Say(Interface):
        def __init__(self, msg: ActorMessage):
            self.name = "say"
            self.msg = msg

        def to_dict(self):
            return {
                "name": "say",
                "msg": self.msg.to_dict()
            }

        @classmethod
        def from_dict(cls, dict):
            return cls(ActorMessage.from_dict(dict["msg"]))

    class Rerun(Interface):
        def __init__(self):
            self.name = "rerun"

        @classmethod
        def from_dict(cls, dict):
            return cls()

    @staticmethod
    def publish_commands(commands: List[Interface]):
        return [c.to_dict() for c in commands]

    @staticmethod
    def decode_commands(commands: List[Dict[str, Any]]):
        c = []
        for command in commands:
            if command["name"] == "do":
                c.append(Command.Do.from_dict(command))
            elif command["name"] == "say":
                c.append(Command.Say.from_dict(command))
            elif command["name"] == "rerun":
                c.append(Command.Rerun.from_dict(command))
            else:
                raise ValueError("command not supported")
        return c


class ActorResponse(Interface):
    def __init__(self,
                 actor: str = None,
                 user_id: str = None,
                 variables: Dict[str, Any] = None,
                 request: str = None,
                 user_message: UserMessage = None):
        self.actor = actor
        self.user_id = user_id
        self.variables = variables
        self.request = request
        self.user_message = user_message

    @classmethod
    def from_dict(cls, response_dict):
        obj = cls()
        obj.actor = response_dict["actor"] if "actor" in response_dict else None
        obj.user_id = response_dict["user_id"] if "user_id" in response_dict else None
        obj.variables = response_dict["variables"] if "variables" in response_dict else None
        obj.request = response_dict["request"] if "request" in response_dict else None
        if "user_message" in response_dict and response_dict["user_message"] is not None:
            obj.user_message = UserMessage.from_dict(response_dict["user_message"])
        else:
            obj.user_message = None
        return obj

    def to_dict(self):
        return {
            "actor": self.actor,
            "user_id": self.user_id,
            "variables": self.variables,
            "request": self.request,
            "user_message": self.user_message.to_dict() if self.user_message is not None else None
        }


class ActionRequest(Interface):
    def __init__(self, name: str, request: UserMessage):
        self.name = name
        self.request = request

    @classmethod
    def from_dict(cls, response_dict):
        return cls(
            response_dict["name"],
            UserMessage.from_dict(response_dict["request"])
        )

    def to_dict(self):
        return {
            "name": self.name,
            "request": self.request.to_dict()
        }


class EventRequest(Interface):
    def __init__(self, request):
        self.name = request["name"]
        self.user_id = request["user_id"]
        self.app_id = request["app_id"]
        self.data = request["data"]
        self.id = request["id"]
