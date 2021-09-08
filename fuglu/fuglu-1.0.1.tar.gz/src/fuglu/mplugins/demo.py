from typing import Union, Tuple
from fuglu.mshared import (
    BMPConnectMixin, BMPHeloMixin, BMPMailFromMixin,
    BMPRCPTMixin, BMPHeaderMixin, BMPEOHMixin, BMPEOBMixin,
    BasicMilterPlugin,
)
from fuglu.connectors.milterconnector import MilterSession, CONTINUE, REJECT, TEMPFAIL


class DemoMPlugin(BMPConnectMixin, BMPHeloMixin, BMPMailFromMixin,
                  BMPRCPTMixin, BMPHeaderMixin, BMPEOHMixin, BMPEOBMixin, BasicMilterPlugin):
    """Demo Milter Plugin with entrypoints for every state"""
    def __init__(self, config, section=None):
        super().__init__(config=config, section=section)
        self.requiredvars = {
            'state': {
                'default': ','.join(BasicMilterPlugin.ALL_STATES.keys()),
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }
        self._counter = 0

    async def examine_connect(self, sess: MilterSession, host: str, addr: str) -> Union[bytes, Tuple[bytes, str]]:
        self.logger.info(f"{sess.id} (connect) host={host}, addr={addr}, queueid={sess.queueid}")
        return CONTINUE

    def examine_helo(self, sess: MilterSession, helo: str) -> Union[bytes, Tuple[bytes, str]]:
        self.logger.info(f"{sess.id} (helo) helo={helo}, queueid={sess.queueid}")
        return CONTINUE

    def examine_mailfrom(self, sess: MilterSession, sender: str) -> Union[bytes, Tuple[bytes, str]]:
        self.logger.info(f"{sess.id} (mailfrom) sender={sender}, queueid={sess.queueid}")
        return CONTINUE

    def examine_rcpt(self, sess: MilterSession, recipient: str) -> Union[bytes, Tuple[bytes, str]]:
        self.logger.info(f"{sess.id} (rcpt) recipient={recipient}, queueid={sess.queueid}")
        self._counter = (self._counter + 1) % 2
        return CONTINUE

    def examine_header(self, sess: MilterSession, key: bytes, value: bytes) -> Union[bytes, Tuple[bytes, str]]:
        self.logger.info(f"{sess.id} (header) header=\"{key}: {value}\", queueid={sess.queueid}")
        #if len(sess.original_headers) > 3:
        #    return REJECT, "too many headers"
        #else:
        #    return CONTINUE
        return CONTINUE

    def examine_eoh(self, sess: MilterSession) -> Union[bytes, Tuple[bytes, str]]:
        self.logger.info(f"{sess.id} (eoh) num headers stored: {len(sess.original_headers)}, queueid={sess.queueid}")
        return CONTINUE

    def examine_eob(self, sess: MilterSession) -> Union[bytes, Tuple[bytes, str]]:
        self.logger.info(f"{sess.id} (eob) mail size: {sess.size} bytes, queueid={sess.queueid}")
        #return REJECT
        return CONTINUE

    def lint(self, state=None):
        print("Hello from Demo Milter Plugin")
        return super().lint(state=state)
