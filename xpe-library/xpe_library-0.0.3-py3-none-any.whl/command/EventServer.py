from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import json


class ProcessEvent(BaseHTTPRequestHandler):
    """
    Class to get and treat device events
    """
    event_list: list = []
    __SERVER_PATH: dict = {
        'rfid': '/rfid',
        'relay': '/relay',
    }

    def do_POST(self):
        """
        Get all POST request and save data in a list

        :return: boolean that represents if request was successful or failed
        """
        content_length: int = int(self.headers['Content-Length'])
        post_data: str = self.rfile.read(content_length).decode()
        if self.path == self.__SERVER_PATH['rfid']:
            self.update_event_list(post_data)
            self.send_response(HTTPStatus.ACCEPTED)
        elif self.path == self.__SERVER_PATH['relay']:
            self.update_event_list(post_data)
            self.send_response(HTTPStatus.ACCEPTED)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
        self.flush_headers()

    def update_event_list(self, data: str):
        """
        updates the list of requests received
        """
        try:
            payload: dict = json.loads(data)
            self.event_list.append(payload)
        except:
            print("error")

    def get_data(self) -> list:
        """
        Get the list that contains all requests received

        :return: list of events
        """
        return self.event_list
