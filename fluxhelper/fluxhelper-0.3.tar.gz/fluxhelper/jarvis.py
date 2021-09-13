"""
Main API interface for jarvis' server.
"""

import datetime as dt
from dataclasses import dataclass, field
from typing import Union

import requests
from dateutil import parser


class ConnectionError(Exception):
    pass


class Dummy(object):

    """
    Dummy object that returns None on every attribute.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __getattr__(self, _):
        return None


class EntityParser:

    """
    Main class for entity parsing. Can be safely extended.
    This is where the entity parsing comes in to play such as converting iso dates to actual datetime objects.
    Both used in the server and clients.

    Parameters
    ----------
    `entity` : str
        name of the entity (actual name not slotName)
    `value` : dict
        the value key from slots
    """

    def __init__(self, entity: str, value: dict):
        self.value_ = value
        self.entity = entity

        self.MAPPINGS = {
            "snips/datetime": self.datetimeParser,
            "snips/duration": self.durationParser,
        }

    @property
    def value(self):
        parsed = self.MAPPINGS.get(self.entity)

        if parsed:
            return parsed()
        return self.value_["value"]

    def datetimeParser(self):
        return parser.parse(self.value_["value"])

    def durationParser(self):
        val = self.value_
        now = dt.datetime.now()
        future = now + dt.timedelta(
            days=val["days"],
            seconds=val["seconds"],
            minutes=val["minutes"],
            hours=val["hours"],
            weeks=val["weeks"],
        )
        return future


@dataclass
class Slot:

    """
    Main data class for slot information. Used both in the server and clients.

    Properties
    ----------
    `value` : the parsed value of the slot/entity
    """

    rawSlot: dict

    entity: str = field(init=False)
    rawValue: str = field(init=False)
    name: str = field(init=False)

    def __post_init__(self):
        self.entity = self.rawSlot["entity"]
        self.rawValue = self.rawSlot["rawValue"]
        self.name = self.rawSlot["slotName"]

    @property
    def value(self):
        return EntityParser(self.entity, self.rawSlot["value"]).value


class API:

    """
    Main API object that connects with jarvis' api.
    """

    def __init__(self, host: str, port: str, logging: object, origin: str = "discord"):
        self.url = f"http://{host}:{port}"
        self.origin = origin
        self.logging = logging

        try:
            r = requests.get(self.url)
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to jarvis' server. Please check your url. ({e})"
            )

        self.apiUrl = self.url + "/api/v1/"

    async def say(self, text: Union[str, list]):

        """
        Make jarvis say something.
        """

        data = {"text": text}

        r = requests.post(self.apiUrl + "say", json=data)
        return r.json()

    async def process(self, text: str, **kwargs):

        """
        Process a text and run the command function connected to the text's intent. This also returns the parsed text.
        """

        data = {"text": text, "origin": self.origin, **kwargs}

        r = requests.post(self.apiUrl + "process", json=data).json()

        if r["data"]:
            return Context(
                self,
                r["data"],
                origin=kwargs.get("origin", self.origin),
                situation=r["data"]["situation"],
                logging=self.logging,
            )
        return None

    async def preprocess(self, text: str, **kwargs):

        """
        Returns a tuple with 3 values, the first one whether the preprocessing passed (ex: starts with prefix/wake word), second one is the original text but stripped, and the third one the modified text (ex: original text with no wake word)
        """

        data = {
            "text": text,
            "situation": kwargs.get("situation", "default"),
            "origin": kwargs.get("origin", self.origin),
        }

        r = requests.post(self.apiUrl + "preprocess", json=data).json()
        if r["data"]:
            return r["data"]["passed"], r["data"]["text"], r["data"]["modified"]
        return False, text, text


@dataclass
class Context:
    """
    Main context object that is returned from API.process when a request succeeds.
    """

    api: API
    parsed: dict
    origin: str
    situation: str
    logging: object

    slots: list = field(init=False)
    probability: list = field(init=False)
    intent: str = field(init=False)
    inp: str = field(init=False)

    def __post_init__(self):
        self.slots = self.parsed["slots"]
        self.probability = self.parsed["intent"]["probability"]
        self.intent = self.parsed["intent"]["intentName"]
        self.inp = self.parsed["input"]

    async def slot(
        self, names: list, slots: list = None, key: str = "slotName"
    ) -> dict:
        """
        Parameters
        ----------
        `names` : list
            List of names to look for. Searching is done by `key`.
        `slots` : list = self.slots
            List of slots that the function will look names for.
        `key` : str = "slotName"
            What key will be used to match with the name.
        """

        if not slots:
            slots = self.slots

        slot_ = [i for i in slots if i[key] in names]
        if not slot_:
            self.logging.debug(f"Slot object value for nmames {names} is None.")
            return None

        slotObj = Slot(slot_[0])
        self.logging.debug(f"Slot object value for names {names} is {slotObj.value}")
        return slotObj
