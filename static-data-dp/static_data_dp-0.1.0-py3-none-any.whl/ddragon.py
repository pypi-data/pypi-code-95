import requests, json
from enum import Enum
import copy
import asyncio
import aiohttp

from .patch import PatchManager

from .DataStore import Champion, Item, Map, Summoner, Icon, Rune


class ddragonFiles(Enum):
    champions = "champion.json"
    championsFull = "championFull.json"
    items = "item.json"
    maps = "map.json"
    summoners = "summoner.json"
    icons = "profileicon.json"
    runes = "runesReforged.json"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


cache = {}


class ddragon(metaclass=Singleton):

    BASE_URL = "http://ddragon.leagueoflegends.com/cdn/"

    def __init__(
        self,
        load=True,
        language="en_US",
        championFull=True,
        baseUrl=None,
        localDirectory=None,
        localVersions=None,
    ):
        self.language = language
        self.championFull = championFull

        if not baseUrl == None:
            self.BASE_URL = baseUrl

        self.LOCAL_DIRECTORY = localDirectory
        self.LOCAL_VERSIONS = localVersions

        self.version = None
        self.pm = None
        if load:
            self.setVersion()

    def setVersion(self, season=None, patch=None, version=None, gameVersion=None):

        if season == None or patch == None or version == None:
            if self.pm == None:
                self.pm = PatchManager(self.LOCAL_VERSIONS)

            if gameVersion == None:
                self.version = self.pm.getVersion(season, patch, version)
            else:
                self.version = self.pm.getVersionFromGameVersion(gameVersion)
        else:
            self.version = "{}.{}.{}".format(season, patch, version)
        self.loadAll()

    def loadAll(self):

        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)

        if self.championFull:
            tasks = [asyncio.ensure_future(self.load(ddragonFiles.championsFull))]
        else:
            tasks = [asyncio.ensure_future(self.load(ddragonFiles.champions))]

        tasks += [
            asyncio.ensure_future(self.load(ddragonFiles.items)),
            asyncio.ensure_future(self.load(ddragonFiles.maps)),
            asyncio.ensure_future(self.load(ddragonFiles.summoners)),
            asyncio.ensure_future(self.load(ddragonFiles.icons)),
            asyncio.ensure_future(self.load(ddragonFiles.runes)),
        ]

        loop.run_until_complete(asyncio.gather(*tasks))

    async def get_data(self, file):
        if self.LOCAL_DIRECTORY == None:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.BASE_URL
                    + self.version
                    + "/data/"
                    + self.language
                    + "/"
                    + file.value
                ) as response:
                    return await response.json()
        else:
            with open(
                self.LOCAL_DIRECTORY
                + self.version
                + "/data/"
                + self.language
                + "/"
                + file.value,
                "r",
            ) as f:
                return json.load(f)

    async def load(self, file):

        if self.version in cache:
            if (
                file == ddragonFiles.champions or file == ddragonFiles.championsFull
            ) and "championById" in cache[self.version]:
                self.championById = cache[self.version]["championById"]
                self.championByName = cache[self.version]["championByName"]
                return

            if file == ddragonFiles.items and "itemById" in cache[self.version]:
                self.itemById = cache[self.version]["itemById"]
                self.itemByName = cache[self.version]["itemByName"]
                return

            if file == ddragonFiles.maps and "mapById" in cache[self.version]:
                self.mapById = cache[self.version]["mapById"]
                self.mapByName = cache[self.version]["mapByName"]
                return

            if (
                file == ddragonFiles.summoners
                and "summonersById =" in cache[self.version]
            ):
                self.summonersById = cache[self.version]["summonersById"]
                self.summonersByName = cache[self.version]["summonersByName"]
                return

            if file == ddragonFiles.icons and "iconsById" in cache[self.version]:
                self.iconsById = cache[self.version]["iconsById"]
                return

            if file == ddragonFiles.runes and "runesById" in cache[self.version]:
                self.runesById = cache[self.version]["runesById"]
                self.runesByName = cache[self.version]["runesByName"]
                return
        else:
            cache[self.version] = {}

        data = await self.get_data(file)

        if file == ddragonFiles.champions or file == ddragonFiles.championsFull:
            self.championById = {}
            self.championByName = {}

            for c in data["data"]:
                champion = Champion(data["data"][c])
                champion.setImageUrl(self.BASE_URL + self.version + "/img/")

                self.championById[int(data["data"][c]["key"])] = champion
                self.championByName[data["data"][c]["name"]] = champion

            cache[self.version]["championById"] = copy.deepcopy(self.championById)
            cache[self.version]["championByName"] = copy.deepcopy(self.championByName)

        if file == ddragonFiles.items:
            self.itemById = {}
            self.itemByName = {}

            for i in data["data"]:
                item = Item(data["data"][i])
                item.setImageUrl(self.BASE_URL + self.version + "/img/")

                self.itemById[int(i)] = item
                self.itemByName[data["data"][i]["name"]] = item

            cache[self.version]["itemById"] = copy.deepcopy(self.itemById)
            cache[self.version]["itemByName"] = copy.deepcopy(self.itemByName)

        if file == ddragonFiles.maps:
            self.mapById = {}
            self.mapByName = {}

            for i in data["data"]:
                m = Map(data["data"][i])
                m.setImageUrl(self.BASE_URL + self.version + "/img/")

                self.mapById[int(i)] = m
                self.mapByName[data["data"][i]["MapName"]] = m

            cache[self.version]["mapById"] = copy.deepcopy(self.mapById)
            cache[self.version]["mapByName"] = copy.deepcopy(self.mapByName)

        if file == ddragonFiles.summoners:
            self.summonersById = {}
            self.summonersByName = {}

            for s in data["data"]:
                summ = Summoner(data["data"][s])
                summ.setImageUrl(self.BASE_URL + self.version + "/img/")

                self.summonersById[int(data["data"][s]["key"])] = summ
                self.summonersByName[data["data"][s]["name"]] = summ

            cache[self.version]["summonersById"] = copy.deepcopy(self.summonersById)
            cache[self.version]["summonersByName"] = copy.deepcopy(self.summonersByName)

        if file == ddragonFiles.icons:
            self.iconsById = {}

            for i in data["data"]:
                icon = Icon(data["data"][i])
                icon.setImageUrl(self.BASE_URL + self.version + "/img/")

                self.iconsById[str(i)] = icon

            cache[self.version]["iconsById"] = copy.deepcopy(self.iconsById)

        if file == ddragonFiles.runes:
            self.runesById = {}
            self.runesByKey = {}

            for tree in data:
                rune = Rune(tree)
                rune.setImageUrl(self.BASE_URL + "img/")

                self.runesById[int(tree["id"])] = rune
                self.runesByKey[tree["key"]] = rune

                for slot in tree["slots"]:
                    for r in slot["runes"]:
                        rune = Rune(r)
                        rune.setImageUrl(self.BASE_URL + "img/")

                        self.runesById[int(r["id"])] = rune
                        self.runesByKey[r["key"]] = rune

            cache[self.version]["runesById"] = copy.deepcopy(self.runesById)
            cache[self.version]["runesByKey"] = copy.deepcopy(self.runesByKey)

    def getChampion(self, champion):
        if isinstance(champion, int) or champion.isdigit():
            return self.championById[int(champion)]
        else:
            return self.championByName[champion]

    def getItem(self, item):
        if isinstance(item, int) or item.isdigit():
            return self.itemById[int(item)]
        else:
            return self.itemByName[item]

    def getMap(self, m):
        if isinstance(m, int) or m.isdigit():
            return self.mapById[int(m)]
        else:
            return self.mapByName[m]

    def getSummoner(self, s):
        if isinstance(s, int) or s.isdigit():
            return self.summonersById[int(s)]
        else:
            return self.summonersByName[s]

    def getIcon(self, icon):
        return self.iconsById[str(icon)]

    def getRune(self, r):
        if isinstance(r, int) or r.isdigit():
            return self.runesById[int(r)]
        else:
            return self.runesByKey[r]

    def withVersion(self, season=None, patch=None, version=None):
        inst = copy.copy(self)
        inst.setVersion(season, patch, version)
        return inst

    def withGameVersion(self, gameVersion):
        inst = copy.copy(self)
        inst.setVersion(gameVersion=gameVersion)
        return inst
