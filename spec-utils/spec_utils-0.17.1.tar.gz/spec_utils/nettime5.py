from urllib.parse import urlparse, urlencode
from base64 import b64encode, b64decode
import requests
import datetime

class Client:
    #nettime_url = None
    access_token = None
    headers = None
    user_rol = None

    def __init__(self, url: str, username: str, pwd: str, *args, **kwargs):
        """ Create a conection with nettime app using recived parameters. """

        super().__init__(*args, **kwargs)
        self.nettime_url = urlparse(url)
        self.username = username
        self.pwd = b64encode(pwd.encode('utf-8'))

        #connect client automatically
        self.connect()

    def __str__(self):
        return '{}{} en {}'.format(
            f'{self.access_token} para ' if self.access_token else '',
            self.username,
            self.nettime_url.geturl()
        )

    def __repr__(self):
        return "{}(url='{}', username='{}', pwd='{}')".format(
            self.__class__.__name__,
            self.nettime_url.geturl(),
            self.username,
            b64decode(self.pwd).decode('utf-8'),
        )

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return self.disconnect()

    @property
    def is_connected(self):
        """ Informs if client has headers and access_token. """

        return bool(self.headers) and bool(self.access_token)
    
    def connect(self):
        """ Connect the client to get access_token and headers values. """

        if self.is_connected:
            return

        url = f'{self.nettime_url.geturl()}/api/login'
        data = {
            "username": self.username,
            "pwd": b64decode(self.pwd).decode('utf-8'),
        }
        response = requests.post(url, data=data)
        
        if response.status_code != 200:
            raise ConnectionError(response.text)

        json_data = response.json()

        if not json_data.get("ok"):
            raise ConnectionError(json_data.get("message"))

        self.access_token = json_data.get("access_token")
        self.headers = self.get_headers()
        self.user_rol = self.get_user_rol()

    def reconnect(self):
        """ Reconnect client cleaning headers and access_token. """

        #clean token and headers for safety
        self.access_token = None
        self.headers = None

        self.connect()

    def get_headers(self):
        """ Return headers for a specific conection """

        if not self.access_token:
            raise ConnectionError("El cliente esta desconectado.")

        return {
            "DNT": "1",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept-Encoding": "gzip,deflate",
            "Cookie": f"sessionID={self.access_token}; i18next=es",
        }

    def disconnect(self):
        """ Disconnect a client to lock the access_token. """

        if not self.is_connected:
            raise ConnectionError("El cliente esta desconectado.")

        url = f'{self.nettime_url.geturl()}/api/logout'
        response = requests.post(url, data="", headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        self.access_token = None
        self.headers = None

    def get_user_rol(self):
        """ Get user_rol of current session. """

        if not self.is_connected:
            raise ConnectionError("El cliente esta desconectado.")

        url = f'{self.nettime_url.geturl()}/api/settings'
        response = requests.get(url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_user_rol()

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)

        json_data = response.json()

        return json_data.get('rol')
    
    def add_clocking(self, employee, date: str, time: str, field: str="id"):
        """ Add a clocking to a employee in a specific date an time. """

        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        if self.user_rol == 'Persona':
            raise ValueError("Método no soportado para el tipo 'Persona'.")
        
        employee_id = int(employee)
        if field != 'id':
            if field.lower() != 'dni':
                raise ValueError(f"No se puede identificar por {field}.")

            employee_id = self.get_employee_id(employee)

        if not employee_id:
            raise ValueError("Error en la búsqueda")

        #time process
        if not isinstance(date, datetime.date):
            date = datetime.date.fromisoformat(date)

        if not isinstance(date, datetime.time):
            time = datetime.datetime.strptime(time, "%H:%M").time()

        date_time = datetime.datetime.combine(date, time)
        
        url = f'{self.nettime_url.geturl()}/api/day/post/'
        json_data = {
            "date": date.isoformat(),
            "clockings": [
                {
                    "id": -1,
                    "type": "timetypes",
                    "date": date_time.isoformat(timespec='milliseconds'),
                    "idReader": -1,
                    "idElem": 0,
                    "status": {"actions": ["Delete", "Edit"]},
                    "_EDIT_DATE": date.isoformat(),
                },
            ],
            "idEmp": employee_id,
        }

        response = requests.post(url, json=json_data, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.add_clocking(employee_id, date, time)

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)

    def get_employee_id(self, dni: str) -> int:
        """ Return DNI of employee from DNI str. """

        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")
        
        url = f'{self.nettime_url.geturl()}/api/user/employees'

        data = {
            "pageStartIndex": 0,
            "pageSize": 50,
            "search": dni,
            "order": "cardId"
        }

        lookup_url = f'{url}?{urlencode(data)}'
        response = requests.get(lookup_url, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.get_employee_id(dni)

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)
        
        json_data = response.json()

        if not json_data.get("total"):
            raise ValueError("No se encuentra el DNI")

        employee_id = 0
        for item in json_data.get("items"):
            if item.get("cardId") == dni:
                employee_id = item.get("id")

        return employee_id
        
    def add_remote_clocking(self, timetype: int=0):
        """ Create a remote clocking if 'user_rol' if 'Persona'. """

        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")
        
        if self.user_rol != 'Persona':
            raise ValueError("Solo Personas pueden usar el marcaje remoto.")

        url = f'{self.nettime_url.geturl()}/api/employee/clocking'

        json_data = {
            "comment": None,
            "elements": [{
                "id": timetype,
                "type": "timetypes",
            }],
            "lat": -1,
            "lon": -1,
            "mobileId": None,
        }

        response = requests.post(url, json=json_data, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.add_remote_clocking(timetype)

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)

    def add_planning(self, employee, dates: list, timetype: int, name: str, \
            comment: str=None):
        """ Add planning to a employee using recived data. """

        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        if self.user_rol == 'Persona':
            raise ValueError("Método no soportado para el tipo 'Persona'.")

        employee_id = int(employee)
        if field != 'id':
            if field.lower() != 'dni':
                raise ValueError(f"No se puede identificar por {field}.")

            employee_id = self.get_employee_id(employee)

        if not employee_id:
            raise ValueError("Error en la búsqueda")
        
        # dates process
        time = datetime.datetime.now().time()
        for _ in range(len(dates)):
            if not isinstance(dates[_], datetime.date):
                dates[_] = datetime.date.fromisoformat(dates[_])
            
            # convert to datetime
            dates[_] = datetime.datetime.combine(dates[_], time)

        url = f'{self.nettime_url.geturl()}/api/planification/post/'
        json_data = {
            "allDay": True,
            "allDayId": timetype,
            "comment": comment,
            "days": [{
                "EndDate": _.isoformat(timespec='milliseconds'),
                "StartDate": _.isoformat(timespec='milliseconds')
            } for _ in dates],
            "id": -1,
            "idEmp": employee_id,
            "name": name,
        }

        response = requests.post(url, json=json_data, headers=self.headers)

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            self.add_clocking(employee_id, date, time)

        # raise if was an error
        if response.status_code != 200:
            raise ConnectionError(response.text)


if __name__ == "__main__":
    
    URL = 'http://localhost:8091'
    USERNAME = '1234'   #employee DNI
    PWD = 'spec.1234'   #employee Password

    client = Client(url=URL, username=USERNAME, pwd=PWD)

    try:
        print("Trying create remote clocking...")
        client.add_remote_clocking()

    except Exception as error:
        print(error)

    finally:
        print("Client disconnecting...")
        client.disconnect()

