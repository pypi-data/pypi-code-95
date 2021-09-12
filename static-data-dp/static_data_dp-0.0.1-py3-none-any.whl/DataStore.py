class DataStore:
    def __init__(self, data):
        self.data = {
            "image": data["image"],
            "name": data["name"],
            "id": data["image"]["full"].split(".")[0],
        }

    def setImageUrl(self, imageUrl):
        self.imageUrl = imageUrl

    @property
    def image(self):
        return (
            self.imageUrl
            + self.data["image"]["group"]
            + "/"
            + self.data["image"]["full"]
        )

    @property
    def sprite(self):
        return (
            self.imageUrl + "sprite/" + self.data["image"]["sprite"],
            self.data["image"]["x"],
            self.data["image"]["y"],
        )

    @property
    def name(self):
        return self.data["name"]

    @property
    def id(self):
        return self.data["id"]


spellToKeyHelper = {0: "Q", 1: "W", 2: "E", 3: "R"}


class Champion(DataStore):
    BASE_URL = "http://ddragon.leagueoflegends.com/cdn/"

    def __init__(self, data):
        self.data = {
            "image": data["image"],
            "name": data["name"],
            "id": data["id"],
            "key": data["key"],
            "spells": [
                {"image": s["image"], "name": s["name"], "id": s["id"]}
                for s in data["spells"]
            ]
            if "spells" in data
            else [],
        }

        self.spellById = None
        if "spells" in self.data:
            self.loadSpells()

    def loadSpells(self):
        self.spellById = {}
        self.spellByName = {}
        self.spellByKey = {}
        self.spellBySlot = {}
        for k, s in enumerate(self.data["spells"]):
            spell = Spell(s)

            self.spellById[s["id"]] = spell
            self.spellByName[s["name"]] = spell
            self.spellByKey[spellToKeyHelper[k]] = spell
            self.spellBySlot[k + 1] = spell

    def spell(self, sp):
        if isinstance(sp, int) or sp.isdigit():
            return self.spellBySlot[int(sp)]
        elif len(sp) == 1:
            return self.spellByKey[sp]
        elif sp in self.spellByName:
            return self.spellByName[sp]
        elif sp in self.spellById:
            return self.spellById[sp]

    def setImageUrl(self, imageUrl):
        self.imageUrl = imageUrl
        if not self.spellById == None:
            for s in self.spellById:
                self.spellById[s].setImageUrl(imageUrl)

    @property
    def key(self):
        return self.data["key"]


class Item(DataStore):
    pass


class Map(DataStore):
    def __init__(self, data):
        self.data = {"image": data["image"], "name": data["MapName"]}


class Summoner(DataStore):
    def __init__(self, data):
        self.data = {
            "image": data["image"],
            "name": data["name"],
            "id": data["id"],
            "key": data["key"],
        }

    @property
    def key(self):
        return self.data["key"]


class Icon(DataStore):
    def __init__(self, data):
        self.data = {"image": data["image"], "name": None}


class Spell(DataStore):
    pass


class Rune:
    def __init__(self, data):
        self.data = {"icon": data["icon"], "name": data["name"], "id": data["id"]}

    def setImageUrl(self, imageUrl):
        self.imageUrl = imageUrl

    @property
    def image(self):
        return self.imageUrl + self.data["icon"]

    @property
    def name(self):
        return self.data["name"]

    @property
    def id(self):
        return self.data["id"]
