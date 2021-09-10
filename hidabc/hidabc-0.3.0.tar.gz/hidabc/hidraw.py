# SPDX-License-Identifier: MIT

import functools
import os

from typing import List

import ioctl.hidraw

import hidabc


class HidrawInterface(hidabc.ExtendedInterface):
    def __init__(self, path: str) -> None:
        self._hidraw = ioctl.hidraw.Hidraw(path)
        self._bus, self._vid, self._pid = self._hidraw.info

    @property
    @functools.lru_cache(maxsize=None)
    def name(self) -> str:
        assert isinstance(self._hidraw.name, str)
        return self._hidraw.name

    @property
    @functools.lru_cache(maxsize=None)
    def phys_name(self) -> str:
        assert isinstance(self._hidraw.phys, str)
        return self._hidraw.phys

    @property
    @functools.lru_cache(maxsize=None)
    def uniq_name(self) -> str:
        assert isinstance(self._hidraw.uniq, str)
        return self._hidraw.uniq

    @property
    def bus(self) -> int:
        assert isinstance(self._bus, int)
        return self._bus

    @property
    def vid(self) -> int:
        assert isinstance(self._vid, int)
        return self._vid

    @property
    def pid(self) -> int:
        assert isinstance(self._pid, int)
        return self._pid

    @property
    @functools.lru_cache(maxsize=None)
    def report_descriptor(self) -> List[int]:
        assert isinstance(self._hidraw.report_descriptor, list)
        return self._hidraw.report_descriptor

    def read(self) -> List[int]:
        return list(os.read(self._hidraw.fd, 1024))  # 1024 is already too much for HID data

    def write(self, data: List[int]) -> None:
        written = os.write(self._hidraw.fd, bytes(data))
        if written != len(data):
            raise IOError(f'Failed to write (expected to write {len(data)} but wrote {written})')
