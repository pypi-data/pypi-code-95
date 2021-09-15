class Interface():
    def to_dict(self):
        return vars(self)


class Text(Interface):
    def __init__(self, mutations):
        if isinstance(mutations, str):
            self.mutations = {"original": mutations}
        else:
            self.mutations = mutations

    def add_mutation(self, key, mutation):
        self.mutations[key] = mutation

    def get(self, key="original"):
        return self.mutations[key]

    def to_dict(self):
        return self.mutations


class Entity(Interface):
    def __init__(self, name, input_type, val, sidx, eidx, confidence) -> None:
        self.name = name
        self.input_type = input_type
        self.val = val
        self.sidx = sidx
        self.eidx = eidx
        self.confidence = confidence


class Intent(Interface):
    def __init__(self, chosen, scores) -> None:
        self.chosen = chosen
        self.scores = scores

    def is_intent_chosen(self):
        return self.chosen is not None

    def confidence(self):
        return self.scores[self.chosen]


class Misc(Interface):
    def __init__(self,
                 button=None,
                 multiselect=None,
                 checkboxes=None,
                 date=None,
                 file=None,
                 latitude=None,
                 longitude=None,
                 nfc=None,
                 form=None
                 ):
        self.button = button
        self.multiselect = multiselect
        self.checkboxes = checkboxes
        self.date = date
        self.file = file
        self.latitude = latitude
        self.longitude = longitude
        self.nfc = nfc
        self.form = form


class UserMessage(Interface):
    def __init__(self, message_dict):
        def is_exist(key, null=None):
            return key in message_dict and message_dict[key] is not null

        self.user_id = message_dict["user_id"]
        self.text = Text(message_dict["text"]) if is_exist("text") else None
        self.misc = Misc(**message_dict["misc"]) if is_exist("misc") else None
        self.intent = Intent(**message_dict["intent"]) if is_exist("intent") else None
        self.entities = [Entity(**e) for e in message_dict["entities"]] if is_exist("entities", []) else []

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "text": self.text.to_dict(),
            "misc": self.misc.to_dict(),
            "intent": self.intent.to_dict(),
            "entities": [e.to_dict() for e in self.entities]
        }
