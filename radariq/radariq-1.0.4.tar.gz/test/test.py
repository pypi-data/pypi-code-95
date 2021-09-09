from struct import unpack
import logging

logging.basicConfig(level=logging.INFO)


def _process_message(msg):
    """
    Process a message onto the python log.
    """
    try:
        message_length = len(msg) - 4
        packing = "<BBBB{}s".format(message_length)
        res = unpack(packing, msg)
        if res[0] == 0x00 and res[1] == 0x01:
            message_type = res[2]
            message_code = res[3]
            message = res[4].decode()
            print(message)
            if message_type in [0, 1]:
                logging.debug('{} {}'.format(message_code, message))
            elif message_type in [2, 5]:
                logging.info('{} {}'.format(message_code, message))
            elif message_type in [3]:
                logging.warning('{} {}'.format(message_code, message))
            elif message_type in [4]:
                logging.error('{} {}'.format(message_code, message))
    except Exception:
        raise Exception("Failed to process message from the RadarIQ sensor")

if __name__ == "__main__":
    text = 'Test message'
    msg = b'\x00\x01\x01\x01' + text.encode()
    print(msg)

    _process_message(msg)