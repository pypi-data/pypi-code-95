# SPDX-License-Identifier: MIT

import functools

from typing import List, Optional

import usb.core
import usb.util

import hidabc


class PyUSBInterface(hidabc.Interface):
    def __init__(
        self,
        device: usb.core.Device,
        interface: int,
        configuration: Optional[int] = None,
    ) -> None:
        if not configuration:
            configuration = device.get_active_configuration().index

        configurations = device.configurations()

        interfaces = configurations[configuration].interfaces()
        if interfaces[interface].bInterfaceClass != 3:  # HID
            raise ValueError(
                f'Specified interface ({interface}), is not HID (expected bInterfaceClass '
                f'to be 3, but got {interfaces[interface].bIntefaceClass})'
            )

        self._endpoint_in, self._endpoint_out = None, None
        endpoints = interfaces[interface].endpoints()
        for endpoint in endpoints:
            if usb.util.endpoint_type(endpoint.bmAttributes) == usb.util.ENDPOINT_TYPE_INTR:
                direction = usb.util.endpoint_direction(endpoint.bEndpointAddress)
                if direction == usb.util.ENDPOINT_IN:
                    self._endpoint_in = endpoint
                elif direction == usb.util.ENDPOINT_OUT:
                    self._endpoint_out = endpoint

        if not self._endpoint_in:
            raise ValueError('Could not find INTERRUPT IN endpoint')

        self._device = device
        self._interface = interface
        self._device.detach_kernel_driver(interface)

    def __del__(self) -> None:
        self._device.attach_kernel_driver(self._interface)

    @property
    def vid(self) -> int:
        assert isinstance(self._device.idVendor, int)
        return self._device.idVendor

    @property
    def pid(self) -> int:
        assert isinstance(self._device.idProduct, int)
        return self._device.idProduct

    @property
    @functools.lru_cache(maxsize=None)
    def report_descriptor(self) -> List[int]:
        return list(self._device.ctrl_transfer(
            bmRequestType=usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_STANDARD,
                usb.util.CTRL_RECIPIENT_INTERFACE,
            ),
            bRequest=0x06,  # GET_DESCRIPTOR
            wValue=0x2200,  # decriptor type = report
            wIndex=self._interface,
            data_or_wLength=0xff,
        ))

    def read(self) -> List[int]:
        assert self._endpoint_in
        return list(self._device.read(self._endpoint_in.bEndpointAddress, 64))

    def write(self, data: List[int]) -> None:
        if not self._endpoint_out:
            raise NotImplementedError('SET_REPORT not implemented')
        written = self._device.write(self._endpoint_out.bEndpointAddress, bytes(data))
        if written != len(data):
            raise IOError(f'Failed to write (expected to write {len(data)} but wrote {written})')
