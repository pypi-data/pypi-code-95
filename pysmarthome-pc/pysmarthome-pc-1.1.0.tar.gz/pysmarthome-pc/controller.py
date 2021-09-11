from pysmarthome import MultiCommandDeviceController, MultiCommandDevicesModel
from pysmarthome import CommandsModel
import wakeonlan
import requests
import json
import os


class PcController(MultiCommandDeviceController):
    model_class = MultiCommandDevicesModel.clone('PcsModel')
    model_class.schema |= {
        'mac_addr': { 'type': 'string' },
        'actions_handler_addr': { 'type': 'string' },
        'actions_handler_api_key': { 'type': 'string' },
    }


    def on(self):
        wakeonlan.send_magic_packet(self.model.mac_addr)


    def off(self):
        self.dispatch('off')


    def send_command(self, id):
        action = CommandsModel.load(id)
        addr = self.model.actions_handler_addr
        api_key = self.model.actions_handler_api_key
        data = action['data']

        return requests.post(
            f'http://{addr}',
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json',
                'API_KEY': api_key,
            },
            data=data,
        )
