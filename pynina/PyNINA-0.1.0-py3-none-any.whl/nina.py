from typing import Dict, Any

from .const import ReadOnlyClass, ENDPOINT_REGIONAL_CODE, ENDPOINT_NINA_BASE
from .baseApi import BaseAPI, ApiError
from .warning import Warning


class Nina(BaseAPI, metaclass=ReadOnlyClass):
    """Main class to interact with the NINA API"""
    def __init__(self):
        """Initialize."""
        self.warnings: Dict[str, list[Any]] = {}
        self.regions: list = []

    def addRegion(self, regionCode: str):
        """Add a region to monitor."""
        if regionCode not in self.regions:
            self.regions.append(regionCode)

    async def update(self):
        """Update the warnings."""
        self.warnings.clear()

        for regionCode in self.regions:
            try:
                url: str = ENDPOINT_NINA_BASE + regionCode + ".json"
                data = await self._makeRequest(url)

                self.warnings[regionCode] = []

                for warn in data:
                    warning: Warning = Warning(warn)
                    self.warnings[regionCode].append(warning)
            except ApiError:
                pass

    async def getAllRegionalCodes(self) -> Dict[str, str]:
        """Fetch all regional codes."""
        rawCodeData: Dict[str, Any] = await self._makeRequest(ENDPOINT_REGIONAL_CODE)

        regionalCodes: Dict[str, str] = {}
        for dataBlock in rawCodeData["daten"]:
            id: str = dataBlock[0]
            name: str = dataBlock[1]

            id = id[:len(id) - 7] + "0000000"

            regionalCodes[name] = id

        return regionalCodes
