import requests
import sys
import datetime
import time

class RequestError(Exception):
    """ Raised when a user send an invalid request to the server """
    pass

class InvalidKey(Exception):
    """ Raised when the API key is invalid """
    pass

class TokenLimit(Exception):
    """ Raised if the user tries to send a request and tokens are finished """
    pass

class Netro:

    base_url = 'https://api.netrohome.com/npa/v1/'

    # Header for every http request made to the server
    header = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json'
    }

    available_commands = {
        'info': 'info.json',
        'schedules': 'schedules.json',
        'moistures': 'moistures.json',
        'events': 'events.json',
        'set_status': 'set_status.json',
        'set_moisture': 'set_moisture.json',
        'water': 'water.json',
        'stop_water': 'stop_water.json',
        'no_water': 'no_water.json'
    }


    def __str__(self):
        return 'Name: ' + self.name + '\n' + 'Status: ' + self.status + '\n' + 'LastUpdate: ' + self.last_update.strftime("%d/%m/%Y %H:%M:%S") + '\n' 'Zones: ' + str(self.zones) + '\n' + 'DeviceEvents: ' + str(self.device_events) + '\n' + 'WateringEvents: ' + str(self.water_events) + '\n'


    def __init__(self, key: str):
        """
        Instantiate a new :class:`Object` of type :class:`Netro` that communicates with Netro API servers using specific key

        :param key: API key used to perform requests
        :raises :class:`UnvalidKey`: if the :param:`key` is not available
        """
        self._key = key
        self._info = self.base_url + self.available_commands['info'] + '?key=' + key
        self._schedules = self.base_url + self.available_commands['schedules'] + '?key=' + key
        self._moistures = self.base_url + self.available_commands['moistures'] + '?key=' + key
        self._events = self.base_url + self.available_commands['events'] + '?key=' + key
        self._set_status = self.base_url + self.available_commands['set_status']
        self._set_moisture = self.base_url + self.available_commands['set_moisture']
        self._water = self.base_url + self.available_commands['water']
        self._stop_water = self.base_url + self.available_commands['stop_water']
        self._no_water = self.base_url + self.available_commands['no_water']

        # Check if the key is correct
        response = requests.get(self._info, headers=self.header)

        # If not then raise an exception
        if not response.status_code == 200:
            self._info = ''
            raise InvalidKey
            return
        
        self.water_events = []
        self.device_events = []
        self.zones = []
        self.last_update = datetime.datetime.now()

        self.tokens_remaining = (response.json()['meta'])['token_remaining']
        self.update_zones()


    def update_info(self):
        self.tokens_remaining -=1
        if not self.tokens_remaining >= 0:
            self._info = ''
            raise TokenLimit
            return

        response = requests.get(self._info, headers=self.header)

        # If not then raise an exception
        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return
        
        for zone in self.zones:
            zone['name'] = ''
            zone['enabled'] = False
            zone['schedules'] = []
            zone['status'] = 'IDLE'

        self.last_update = datetime.datetime.now()
        self.name  = (response.json()['data'])['device']['name']
        self.status  = (response.json()['data'])['device']['status']
        self.zones = [{}] * ((response.json()['data'])['device']['zone_num'])
        for zone in (response.json()['data'])['device']['zones']:
            self.zones[zone['ith'] - 1] = {
                'name': zone['name'],
                'enabled': zone['enabled'],
                'smart': zone['smart'],
                'status': 'IDLE',
                'schedules': [],
                'moisture': 0,
                'moisture_date': '0000-00-00'
            }
    

    def update_schedules(self):
        self.tokens_remaining -=1
        if not self.tokens_remaining >= 0:
            self._schedules = ''
            raise TokenLimit
            return

        response = requests.get(self._schedules, headers=self.header)

        # If not then raise an exception
        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return

        for zone in self.zones:
            zone['schedules'] = []
            zone['status'] = 'IDLE'

        self.last_update = datetime.datetime.now()
        for schedule in (response.json()['data'])['schedules']:
            if schedule['status'] == 'EXECUTING' and (datetime.datetime.strptime(schedule['local_date'], "%Y-%m-%d")).date() == datetime.datetime.today().date():
                (self.zones[schedule['zone'] - 1])['status'] = 'WATERING'
                print((self.zones[schedule['zone'] - 1]))
            (self.zones[schedule['zone'] - 1])['schedules'].append({
                'date': schedule['local_date'],
                'start_time': schedule['local_start_time'],
                'end_time': schedule['local_end_time'],
                'source': schedule['source']
            })


    def update_moistures(self):
        self.tokens_remaining -=1
        if not self.tokens_remaining >= 0:
            self._schedules = ''
            raise TokenLimit
            return

        response = requests.get(self._moistures, headers=self.header)

        # If not then raise an exception
        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return
        
        for zone in self.zones:
            zone['moisture'] = 0
            zone['moisture_date'] = '0000-00-00'

        self.last_update = datetime.datetime.now()
        for moisture in (response.json()['data'])['moistures']:
            if (self.zones[moisture['zone'] - 1])['moisture_date'] < moisture['date']:
                (self.zones[moisture['zone'] - 1])['moisture'] = moisture['moisture']
                (self.zones[moisture['zone'] - 1])['moisture_date'] = moisture['date']


    def update_events(self):
        self.tokens_remaining -=1
        if not self.tokens_remaining >= 0:
            self._schedules = ''
            raise TokenLimit
            return

        response = requests.get(self._events, headers=self.header)

        # If not then raise an exception
        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return
        
        self.last_update = datetime.datetime.now()
        for event in (response.json()['data'])['events']:
            if event['event'] == 1 or event['event'] == 2:
                self.device_events.append({
                    'time': event['time'],
                    'message': event['message'],
                })  
            if event['event'] == 3 or event['event'] == 4:
                self.water_events.append({
                    'time': event['time'],
                    'message': event['message'],
                }) 
               

    def update_zones(self):
        self.update_events()
        self.update_info()
        self.update_moistures()
        self.update_schedules()


    def set_status(self, status: bool = True) -> bool:
        # Check if the user wants the device to be turned on or off
        status = '1' if status else '0'
        data = '{"key":"' + self._key + '",' + '"status":' + status + '}'
        
        response = requests.post(self._set_status, data=data, headers=self.header)

        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return

        time.sleep(2)
        self.update_info()
        return True if response.json()['status'] == 'OK' else False


    def water(self, delay: int = 0, duration: int = 15, zone: int = 0) -> bool:
        if zone == 0:
            data = '{"key":"' + self._key + '",' + '"duration":' + str(duration) + ',"delay":' + str(delay) + '}'
        else:
            data = '{"key":"' + self._key + '",' + '"duration":' + str(duration) + ',"delay":' + str(delay) + ',"zones":[' + str(zone + 1) + ']}'

        response = requests.post(self._water, data=data, headers=self.header)

        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return

        time.sleep(2)
        self.update_schedules()
        return True if response.json()['status'] == 'OK' else False


    def stop_water(self) -> bool:
        self.update_schedules()
        data = '{"key":"' + self._key + '"}'
        response = requests.post(self._stop_water, data=data, headers=self.header)

        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return

        time.sleep(2)
        self.update_schedules()
        return True if response.json()['status'] == 'OK' else False


    def no_water(self, days: int = 1) -> bool:
        data = '{"key":"' + self._key + ', "days":' + str(days) + '}'
        
        response = requests.post(self._stop_water, data=data, headers=self.header)

        if not response.status_code == 200:
            self._host = ''
            raise RequestError
            return

        time.sleep(2)
        self.update_schedules()
        return True if response.json()['status'] == 'OK' else False
