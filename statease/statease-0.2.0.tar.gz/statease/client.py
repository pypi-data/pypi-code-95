import zmq
import json
import base64
import zlib
import logging
from .response import Response
from .factor import Factor
from .analysis import Analysis
from .optimizer import Optimizer

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

class HTTPException(IOError):

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', 500)
        super().__init__(*args, **kwargs)

class SEClient:

    REQUEST_TIMEOUT = 2500
    REQUEST_RETRIES = 3
    SERVER_ENDPOINT = "tcp://localhost:4900"

    def __init__(self):
        self.connect()

    def connect(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(self.SERVER_ENDPOINT)

    def status_ok(self, reply):
        return reply.get('status', 500) < 400

    def decode_payload(self, payload):
        payload_bytes = base64.b64decode(payload)
        return json.loads(zlib.decompress(payload_bytes))

    def send_payload(self, payload):

        self.socket.send_json(payload)
        retries_left = self.REQUEST_RETRIES
        while True:
            if (self.socket.poll(self.REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = self.socket.recv_json()

                if self.status_ok(reply):
                    if reply.get('payload', None):
                        reply['payload'] = self.decode_payload(reply['payload'])
                    retries_left = self.REQUEST_RETRIES
                    break
                else:
                    if reply.get('payload', None):
                        error_msg = self.decode_payload(reply['payload'])
                        raise HTTPException("Received error from Stat-Ease 360: {}".format(error_msg), status=reply.get('status', 500))
                    raise HTTPException("Received invalid response from Stat-Ease 360: {}".format(reply), status=reply.get('status', 500))

            retries_left -= 1
            # socket is confused, close and remove
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            if retries_left == 0:
                raise HTTPException("No response from Stat-Ease 360 after {} attempts.".format(self.REQUEST_RETRIES), status=500)
            logging.warning("No response from Stat-Ease 360, retrying...")

            # reconnect and re-send
            self.connect()
            self.socket.send_json(payload)

        return reply

    def prompt(self, message):
        self.send_payload({
            "method": "POST",
            "uri": "prompt",
            "message": message,
        })

    def go_to_node(self, node, analysis_name):
        self.send_payload({
            "method": "POST",
            "uri": "nodes",
            "node": str(node),
            "analysis": analysis_name,
        })

    def open_design(self, path = ""):
        self.send_payload({
            "method": "POST",
            "uri": "open",
            "path": path,
        })

    def list_analyses(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "analysis",
        })

        return result['payload']['analyses']

    def get_analysis(self, name):
        return Analysis(self, name)

    def get_optimizer(self):
        return Optimizer(self)

    def create_analysis(self, response_name, analysis_name):

        reply = self.send_payload({
            "method": "POST",
            "uri": "analysis/create",
            "response_name": response_name,
            "analysis_name": analysis_name
        })

        return Analysis(self, analysis_name)

    def list_responses(self):
        """Returns a list of all response names in the current design.

        Use :func:`get_response` to retrieve response settings and row data.

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.list_responses()
            ["R1", "R2"]
        """
        result = self.send_payload({
            "method": "GET",
            "uri": "design/response",
        })

        return result['payload']['responses']

    def get_response(self, name):
        """Retrieves a response from the current design.

        :param str name: The name of the response. Case insensitive.
        :rtype: statease.response.Response

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.get_response("CFU")
            name: “CFU”
            units: “per cm^2”
            length: 20
        """
        return Response(self, name)

    def list_factors(self):
        """Returns a list of all factor names in the current design.

        Use :func:`get_factor` to retrieve factor settings and row data.

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.list_factors()
            ["A", "B", "C"]
        """
        result = self.send_payload({
            "method": "GET",
            "uri": "design/factor",
        })

        return result['payload']['factors']

    def get_factor(self, name):
        """Retrieves a factor from the current design.

        :param str name: The name of the factor. Case insensitive.
        :rtype: statease.factor.Factor

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.get_factor("n-propanol")
            name: “N-Propanol”
            units: “wt %”
            length: 20
        """
        return Factor(self, name)

    def get_design_model(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/model",
        })

        return result['payload']['model']

