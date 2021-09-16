import networkbilling.vic as vic
import networkbilling.nsw as nsw
import networkbilling.qld as qld
import networkbilling.sa as sa
import networkbilling.base as base

import csv
import io
import pathlib
import datetime
import re
from typing import Any, Callable, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class FileName:
    distributor: str
    retailer: str
    timestamp: datetime.datetime
    version: Optional[int]
    state: str

    @staticmethod
    def parse(filename: str) -> 'FileName':
        # some participants use `#` as the seperator while others use `_`. Allow for both here.
        # some participants use lowercase, `(?i)` makes the regex case insensitive
        # some participants drop the `v[0-9]` on the end, make it optional as we don't use it anyway
        matches = re.match("(?i)NEM[_#]NBCHARGES[_#]([A-Z]+)[_#]([A-Z]+)[_#]([0-9]{14})V?([0-9]+)?", filename)
        distributor_mapping = {
            "ENERGEXP": "qld",
            "ERGONETP": "qld",
            "UMPLP": "sa",
            "ETSATP": "sa",
            "ENERGYAP": "nsw",
            "CNRGYP": "nsw",
            "INTEGP": "nsw",
            "CITIPP": "vic",
            "POWCP": "vic",
            "SOLARISP": "vic",
            "UNITED": "vic",
            "EASTERN": "vic",
        }
        if matches is not None and matches.group(1).upper() in distributor_mapping.keys():
            if matches.group(4) is None:
                version = None
            else:
                version = int(matches.group(4))
            return FileName(
                distributor=matches.group(1).upper(),
                retailer=matches.group(2).upper(),
                timestamp=datetime.datetime.strptime(matches.group(3), "%Y%m%d%H%M%S"),
                version=version,
                state=distributor_mapping[matches.group(1).upper()]
            )
        else:
            raise base.InvalidFilename("File name {} did not match the expected format".format(filename))

    def get_header_mapping(self) -> Callable[[int], Any]:
        if self.state == 'nsw':
            return nsw.header_mapping
        elif self.state == 'qld':
            return qld.header_mapping
        elif self.state == 'vic':
            return vic.header_mapping
        elif self.state == 'sa':
            return sa.header_mapping
        else:
            raise base.UnsupportedState


def from_filesystem(path: pathlib.Path) -> Any:
    with open(path, 'r') as f:
        filename = FileName.parse(path.name)
        reader = csv.reader(f)
        data = list(reader)
        header_record_type = int(data[0][0])
        return filename.get_header_mapping()(header_record_type)(data)


def from_str(filename: FileName, f: str) -> Any:
    reader = csv.reader(io.StringIO(f))
    data = list(reader)
    header_record_type = int(data[0][0])
    return filename.get_header_mapping()(header_record_type)(data)
