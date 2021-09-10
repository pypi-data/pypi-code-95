from typing import Optional

from .client import XiqBaseClient


class XiqDevices(XiqBaseClient):
    """
    APIs as defined:
    https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config#/Device
    """

    async def fetch_devices(self, page_sz: Optional[int] = None):
        """
        This coroutine is used to retrieve the complete list of devieces.
        The optional page_sz argument determeines the number of devices to
        fetch during pagination.

        Parameters
        ----------
        page_sz: int page size for pagination

        Returns
        -------
        List[dict] - List of device records
        """
        return await self.paginate("/devices", page_sz=page_sz)
