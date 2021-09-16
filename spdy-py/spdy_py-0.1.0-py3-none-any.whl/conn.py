import io
import logging
from typing import Dict
import zlib

from . import dictionary

LOG = logging.getLogger(__name__)


# control frame types
SYN_STREAM = 1
SYN_REPLY = 2
RST_STREAM = 3
SETTINGS = 4
PING = 6
GOAWAY = 7
HEADERS = 8
WINDOW_UPDATE = 9


class IncompleteRead(Exception):
    pass


class Framer:
    def __init__(self):
        self.buffer = bytearray()
        self.inflate = zlib.decompressobj(zdict=dictionary.zdict)
        self.deflate = None

    def read_frames(self, b):
        self.buffer.extend(b)

        frames = []
        try:
            frame = self._read_frame()
            while frame:
                frames.append(frame)
                frame = self._read_frame()

        except IncompleteRead:
            return frames

    def _read_frame(self):
        buf = self.buffer

        if len(buf) < 8:
            # incomplete buffer
            raise IncompleteRead()

        header = buf[0:8]

        control = header[0] & int("10000000", 2)
        control = control >> 7

        frame = {}
        frame["control"] = control

        if control:
            b = header[0] & int("01111111", 2)
            byt = bytearray()
            byt.append(b)
            byt.extend(bytes(header[1:2]))
            frame["version"] = int.from_bytes(byt, "big")
            frame["type"] = int.from_bytes(header[2:4], "big")
        else:
            frame["stream_id"] = read_stream_id(buf[0:4])

        frame["flags"] = header[5]
        length = int.from_bytes(header[5:8], "big")
        frame["length"] = length

        if len(buf) < 8 + length:
            # incomplete buffer
            raise IncompleteRead()

        data = bytes(buf[8 : length + 8])
        frame["data"] = data

        self.buffer = buf[length + 8 :]

        if control:
            unpack_control_frame(frame)
            del frame["data"]
            if "_header_block" in frame:
                frame["headers"] = read_header_block(
                    frame["_header_block"], self.inflate
                )
                del frame["_header_block"]

        return frame


def read_stream_id(b):
    if len(b) < 4:
        raise ValueError("Need at least 4 bytes to unpack")

    f = b[0] & int("01111111", 2)
    byt = bytearray()
    byt.append(f)
    byt.extend(bytes(b[1:4]))
    return int.from_bytes(byt, "big")


def unpack_control_frame(frame: Dict):
    t2f = {
        SYN_STREAM: read_syn_stream,
        SYN_REPLY: read_syn_reply,
        RST_STREAM: read_rst_stream,
        SETTINGS: read_settings,
        PING: read_ping,
        GOAWAY: read_goaway,
        HEADERS: read_headers,
        WINDOW_UPDATE: read_window_update,
    }

    fn = t2f.get(frame["type"])
    if fn:
        return fn(frame)
    else:
        raise AssertionError("Unrecognized control frame type: type=%s" % frame["type"])


def read_syn_stream(frame):
    data = frame["data"]

    new_stream_id = read_stream_id(data[:4])
    asso_stream_id = read_stream_id(data[4:8])

    priority = data[8] & int("11100000", 2)
    priority = priority >> 5

    slot = data[9]

    header_block = data[10:]

    ex = {
        "stream_id": new_stream_id,
        "associated_to_stream_id": asso_stream_id,
        "priority": priority,
        "slot": slot,
        "_header_block": header_block,
    }

    frame.update(ex)
    return frame


def read_header_block(headers_block, inflate):
    header_bytes = inflate.decompress(headers_block)
    header_bytes += inflate.flush(zlib.Z_SYNC_FLUSH)

    h = io.BytesIO(header_bytes)

    headers = {}
    pairs = int.from_bytes(h.read(4), "big")
    for i in range(pairs):
        nl = int.from_bytes(h.read(4), "big")
        name = h.read(nl).decode("ascii")
        vl = int.from_bytes(h.read(4), "big")
        val = h.read(vl).decode("ascii")
        headers[name] = val

    return headers


def read_syn_reply(frame):
    data = frame["data"]

    ex = {
        "stream_id": read_stream_id(data[:4]),
        "_header_block": data[4:],
    }
    frame.update(ex)
    return frame


def read_rst_stream(frame):
    data = frame["data"]
    ex = {
        "stream_id": read_stream_id(data[:4]),
        "status_code": int.from_bytes(data[4:8], "big"),
    }
    frame.update(ex)
    return frame


def read_settings(frame):
    pass


def read_ping(frame):
    data = frame["data"]
    ex = {
        "id": int.from_bytes(data[:4], "big"),
    }
    frame.update(ex)
    return frame


def read_goaway(frame):
    # structure is the same
    return read_rst_stream(frame)


def read_headers(frame):
    # structure is the same
    return read_syn_reply(frame)


def read_window_update(frame):
    data = frame["data"]
    ex = {
        "stream_id": read_stream_id(data[:4]),
        # delta window size is also a 31bit integer, like stream_ids
        "delta_window_size": read_stream_id(data[4:8]),
    }
    frame.update(ex)
    return frame
