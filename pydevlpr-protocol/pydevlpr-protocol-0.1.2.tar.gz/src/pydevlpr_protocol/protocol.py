import logging
import struct
from typing import Union, Tuple, List
from asyncio.streams import StreamReader, StreamWriter


class DaemonSocket:
    """Daemon specific socket wrapper for Asyncio's TCP socket implementation."""

    def __init__(self, reader, writer):
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer
        self.remote_address = writer.get_extra_info('peername')  # FIXME Not clear what all the type options are here

    def get_remote_address(self):
        """Gests the address of socket, this includes IP and port along with protocol dependent info.
        
        Find a list of return values here: """

        return self.remote_address

    def closed(self) -> bool:
        """Checks if socket is closed."""

        return self.writer.is_closing()

    async def close(self) -> None:
        """Blocking socket close."""

        self.writer.close()
        await self.writer.wait_closed()

    async def send(self, msg: str) -> None:
        """Sends a message on the socket, assumes no '\\n' character included."""

        # make sure we're not closed before trying to write
        if self.closed():
            return
        msg += "\n"
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def recv(self) -> str:
        """Blocking read of data stream from socket until a '\\n' is observed."""

        # make sure we're not closed before trying to read
        if self.closed():
            return ''
        msg = await self.reader.readline()
        return msg.decode().strip()

class DataFormatException(Exception):
    """Exception thrown when protocol.py conversions fail."""

    pass

class PacketType:
    """Shorthands for the packet types the daemon sends/recvs.
    
    PacketTypes must be 1 character to avoid overlap with DataTopic.
    """

    SUBSCRIBE = "s"
    DATA = "d"
    UNSUBSCRIBE = "u"

    @staticmethod
    def topics() -> List[str]:
        """Returns a list of all possible packet types."""

        return [val for attr, val in vars(PacketType).items() if not callable(getattr(PacketType, attr)) and not attr.startswith("__")]

class DataTopic:
    """Shorthands for each of the supported topics.
    
    All DataTopics should be 2 characters to avoid overlap with PacketType.
     """
    
    RAW_DATA_TOPIC = "ra"
    FLEX_TOPIC     = "fl"
    PEAK_TO_PEAK_TOPIC = "pp"
    PEAK_AMP_TOPIC  = "pa"
    WINDOW_AVG_TOPIC = "wa"
    NOTCH_60_TOPIC = "60"
    NOTCH_50_TOPIC = "50"

    @staticmethod
    def topics() -> List[str]:
        """Returns a list of all possible data topics."""

        return [val for attr, val in vars(DataTopic).items() if not callable(getattr(DataTopic, attr)) and not attr.startswith("__")]


DELIM = "|"  # Agreed upon protocol delimiter with daemon/plugin

def wrap_packet(msg_type: str, *data: Tuple[Union[str, int]]) -> str:
    """Packages the messages in the way that the daemon expects."""

    topics = DataTopic.topics()
    packet_types = PacketType.topics()
    if msg_type not in topics and msg_type not in packet_types:
        logging.error("Unsupported message, see DataTopic or PacketType")
        raise DataFormatException
    return "{}{}{}".format(msg_type, DELIM, DELIM.join([str(d) for d in data]))

def unwrap_packet(msg: str) -> Union[Tuple[str, str], Tuple[str, int, str]]:
    """Extracts the data, pin and topic from the incoming message from the daemon."""

    try:
        unwrapped = str(msg).split(DELIM, maxsplit=2)
    except TypeError:
        logging.warning("Invalid Message Type")
        raise DataFormatException
    
    # Command Message
    if len(unwrapped) == 2:
        try:
            return (unwrapped[0], unwrapped[1])
        except IndexError:
            logging.warning("Invalid Message - msg: {!r}, unwrapped: {}".format(msg, unwrapped))
            raise DataFormatException
    # Data Message
    elif len(unwrapped) == 3:
        try:
            pin = int(unwrapped[1])
        except ValueError:
            logging.error("Invalid pin value: {}".format(unwrapped[1]))
            pin = -1
        return (unwrapped[0], pin, unwrapped[2])
    else:
        raise DataFormatException

def unpack_serial(byte_array: bytes) -> Tuple[int, int]:
    """Takes an incoming serial, bitpacked message from the DEVLPR and formats it for the daemon."""

    if len(byte_array) != 3:
        logging.warning("Invalid Message - {!r}".format(byte_array))
        raise DataFormatException
    try:
        # create a temporary bytearray to unpack our weird protocol
        # bit packing in 3 bytes for emg (16 bit) and pin (4 bit) follows:
        # eeee eee0
        # eeee eee0
        # eepp pp00
        tmp = bytearray([0,0,0])
        tmp[0] = byte_array[0] | (byte_array[1] >> 7)
        tmp[1] = ((byte_array[1] << 1) & 0xFF) | (byte_array[2] >> 6)
        tmp[2] = (byte_array[2] >> 2) & 0x0F
        data,pin = struct.unpack('>hB', tmp)
    except IndexError:
        logging.warning("Invalid Message")
        raise DataFormatException
    return (pin, data)
