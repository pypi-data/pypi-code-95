

import logging

from typing import List
from typing import Optional
from pydantic import Field
from pydantic import BaseModel
from fastapi import Body
from fastapi import Depends
from fastapi import APIRouter
from fastapi import HTTPException

from wpasupplicantconf import WpaSupplicantConf

from ebs.linuxnode.netconfig import config
from ebs.linuxnode.netconfig.core import app
from ebs.linuxnode.netconfig.core import auth_token
from ebs.linuxnode.netconfig.core import ActionResultModel

logger = logging.getLogger(__name__)
WPA_SUPPLICANT_PATH = config.wpa_supplicant_path

wifi_router = APIRouter(prefix='/wifi',
                        dependencies=[Depends(auth_token)])


class WiFiScanProxy(object):
    pass


class WifiNetworkModel(BaseModel):
    ssid: str = Field(None, title="Wifi SSID")
    psk: str = Field(None, title="Wifi PSK (WPA2)")


class WPASupplicantProxy(object):
    def __init__(self, cpath='/etc/wpa_supplicant/wpa_supplicant.conf'):
        self._cpath = cpath
        self._config = self._read_config()

    def _read_config(self):
        logger.info("Reading WPA supplicant configuration from {}".format(self._cpath))
        with open(self._cpath, 'r') as f:
            lines = f.readlines()
            return WpaSupplicantConf(lines)

    def _write_config(self):
        logger.info("Writing WPA supplicant configuration to {}".format(self._cpath))
        with open(self._cpath, 'w') as f:
            self._config.write(f)

    def show_networks(self):
        networks = self._config.networks()
        return [WifiNetworkModel(ssid=k, psk=v['psk'])
                for k, v in networks.items()]

    def has_network(self, ssid):
        return ssid in self._config.networks()

    def add_network(self, ssid, psk, **kwargs):
        logger.info("Adding WiFi network '{}' with psk '{}'".format(ssid, psk))
        psk = '"{}"'.format(psk)
        self._config.add_network(ssid, psk=psk, key_mgmt="WPA-PSK", **kwargs)
        self._write_config()

    def remove_network(self, ssid):
        logger.info("Removing WiFi network '{}'".format(ssid))
        self._config.remove_network(ssid)
        self._write_config()


_wpa_supplicant: Optional[WPASupplicantProxy] = None


@app.on_event('startup')
async def init():
    global _wpa_supplicant
    _wpa_supplicant = WPASupplicantProxy(WPA_SUPPLICANT_PATH)


@wifi_router.get("/networks/show", response_model=List[WifiNetworkModel], status_code=200)
async def show_configured_wifi_networks():
    networks = _wpa_supplicant.show_networks()
    logger.info("Currently configured networks :\n{}".format(
        "\n".join(["{:20} {}".format(x.ssid, x.psk)
                   for x in networks])))
    return networks


@wifi_router.post("/networks/add", response_model=ActionResultModel, status_code=201)
async def add_wifi_network(network: WifiNetworkModel):
    if _wpa_supplicant.has_network(network.ssid):
        raise HTTPException(
            status_code=409,
            detail="SSID '{}' already exists. Modify the existing network or remove it and try again."
                   "".format(network.ssid)
        )
    _wpa_supplicant.add_network(ssid=network.ssid, psk=network.psk)
    return {"result": True}


@wifi_router.post("/networks/remove", response_model=ActionResultModel, status_code=200)
async def remove_wifi_network(ssid: str = Body(...)):
    if not _wpa_supplicant.has_network(ssid):
        raise HTTPException(
            status_code=416,
            detail="SSID '{}' not recognized. Cannot remove.".format(ssid)
        )
    _wpa_supplicant.remove_network(ssid=ssid)
    return {"result": True}


@wifi_router.get("/status")
async def wifi_network_status():
    return {"message": "WNS"}


@wifi_router.get("/scan")
async def scan_wifi_networks():
    return {"message": "SN"}
