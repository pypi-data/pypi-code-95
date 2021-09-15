from os import mkdir
from os.path import exists, dirname
from sqlite3 import connect
from datetime import datetime, timedelta
from sqlite3 import Connection
from sqlite3.dbapi2 import ProgrammingError
from typing import Set
from uuid import UUID
from urllib.parse import urljoin
from requests import post
from requests.exceptions import ConnectionError

from .model import Setting, Timespan
from .serializer import TimespanSerializer

class DatabaseHandler():
    def __init__(self, database_connection):
        self.is_testing = False
        if type(database_connection) is Connection:
            self.connection = database_connection
            self.is_testing = True
        else:
            if not exists(database_connection):
                directory = dirname(database_connection)
                if directory != '' and not exists(directory):
                    mkdir(directory)
            self.connection = connect(database_connection, check_same_thread=False)
        cursor = self.connection.execute('SELECT count(*) FROM sqlite_master WHERE type="table" AND name="timespans";')
        if cursor.fetchone()[0] == 0:
            self.connection.execute('CREATE TABLE timespans (id TEXT NOT NULL PRIMARY KEY, start_time DATETIME, stop_time DATETIME);')
            self.connection.commit()
        cursor = self.connection.execute('SELECT count(*) FROM sqlite_master WHERE type="table" AND name="settings";')
        if cursor.fetchone()[0] == 0:
            self.connection.execute('CREATE TABLE settings (id TEXT NOT NULL PRIMARY KEY, key TEXT, value TEXT);')
            self.connection.execute('CREATE INDEX key_index ON settings (key);')
            self.connection.commit()

    def __del__(self):
        if not self.is_testing:
            self.connection.close()

    def get_tracked_time_in_seconds(self) -> timedelta:
        daily_sum_in_seconds = timedelta(seconds=0)
        cursor = self.connection.execute('SELECT round(sum((julianday(stop_time) - julianday(start_time)) * 24 * 60 * 60)) as timespan FROM timespans WHERE date("now") = date(start_time);')
        response = cursor.fetchone()[0]
        if response != None:
            daily_sum_in_seconds = timedelta(seconds=response)
        self.connection.commit()
        return daily_sum_in_seconds

    def save_timespan(self, timespan: Timespan):
        if type(timespan) is not Timespan:
            raise ValueError

        if timespan.start_time is None:
            raise ValueError

        select_statement = 'SELECT COUNT(*) FROM timespans WHERE id="%s"' % timespan.id
        cursor = self.connection.execute(select_statement)
        if cursor.fetchone()[0] > 0:
            delete_statement = 'DELETE FROM timespans WHERE id="%s"' % timespan.id
            self.connection.execute(delete_statement)
        insert_statement = 'INSERT INTO timespans VALUES ("%s", "%s", "%s")' % (timespan.id, timespan.start_time, timespan.stop_time)
        self.connection.execute(insert_statement)
        self.connection.commit()

    def get_recent_timespan(self) -> Timespan:
        cursor = self.connection.execute('SELECT * FROM timespans WHERE stop_time = "None";')
        response = cursor.fetchone()
        timespan = Timespan()
        if response is not None:
            timespan.id = response[0]
            timespan.start_time = datetime.strptime(response[1], '%Y-%m-%d %H:%M:%S.%f')
            return timespan
        return None

    def save_setting(self, setting: Setting):
        if type(setting) is not Setting:
            raise ValueError

        if setting.key is None:
            raise ValueError

        select_statement = 'SELECT COUNT(*) FROM settings WHERE key="%s"' % setting.key
        cursor = self.connection.execute(select_statement)
        if cursor.fetchone()[0] > 0:
            delete_statement = 'DELETE FROM settings WHERE key="%s"' % setting.key
            self.connection.execute(delete_statement)
        insert_statement = 'INSERT INTO settings VALUES ("%s", "%s", "%s")' % (setting.id, setting.key, setting.value)
        self.connection.execute(insert_statement)
        self.connection.commit()

    def read_setting(self, key: str) -> Setting:
        if not key:
            return

        select_statement = 'SELECT * FROM settings WHERE key="%s"' % key
        cursor = self.connection.execute(select_statement)
        row = cursor.fetchone()
        if row is None:
            raise KeyError

        setting = Setting()
        setting.id = UUID(row[0])
        setting.key = row[1]
        setting.value = row[2]
        return setting

    def delete_setting(self, key: str):
        if not key:
            return

        select_statement = 'SELECT * FROM settings WHERE key="%s"' % key
        cursor = self.connection.execute(select_statement)
        row = cursor.fetchone()
        if row is None:
            return
        else:
            delete_statement = 'DELETE FROM settings WHERE key="%s"' % key
            self.connection.execute(delete_statement)
            self.connection.commit()

class TimeslimeHandler():
    def __init__(self, daily_working_time, database_handler, timeslime_server_handler = None):
        self.daily_working_time = daily_working_time
        self.database_handler = database_handler
        self.timeslime_server_handler = timeslime_server_handler
        self.timespan = self.database_handler.get_recent_timespan()
        self.on_start = None
        self.on_stop = None

    def start_time(self):
        self.stop_time()
        self.timespan = Timespan()
        self.timespan.start_time = datetime.now()
        self.database_handler.save_timespan(self.timespan)
        if self.timeslime_server_handler is not None:
            try:
                self.timeslime_server_handler.send_timespan(self.timespan)
            except ConnectionError:
                pass
        if self.on_start is not None:
            self.on_start()

    def stop_time(self):
        if self.timespan is not None and self.timespan.start_time is not None and self.timespan.stop_time is None:
            self.timespan.stop_time = datetime.now()
            self.database_handler.save_timespan(self.timespan)
            if self.timeslime_server_handler is not None:
                try:
                    self.timeslime_server_handler.send_timespan(self.timespan)
                except ConnectionError:
                    pass
        if self.on_stop is not None:
            self.on_stop()

    def get_elapsed_time(self) -> bool:
        daily_sum_in_seconds = self.database_handler.get_tracked_time_in_seconds()
        current_timedelta = timedelta(seconds=0)
        if self.timespan is not None and self.timespan.stop_time is None:
            current_timedelta = datetime.now() - self.timespan.start_time
        return self.daily_working_time - daily_sum_in_seconds - current_timedelta

    def is_running(self):
        if self.database_handler.get_recent_timespan() is not None:
            return True
        else:
            return False

class TimeslimeServerHandler():
    def __init__(self, server_url):
        self.server_url = server_url
        self.timespan_route = urljoin(self.server_url, "api/v1/timespans")

    def send_timespan(self, timespan: Timespan) -> Timespan:
        if timespan is None or timespan.start_time is None:
            raise TypeError

        if not self.server_url:
            return timespan

        timespan_serializer = TimespanSerializer()
        data = timespan_serializer.serialize(timespan)
        response = post(self.timespan_route, headers = {'Content-Type': 'application/json'}, data = data)
        response.raise_for_status()
        response_timespan = timespan_serializer.deserialize(response.text)

        return response_timespan

class SettingsHandler():
    def __init__(self, database_handler: DatabaseHandler):
        self.database_handler = database_handler

    def set(self, key: str, value: str):
        setting = Setting()
        setting.key = key
        setting.value = value
        self.database_handler.save_setting(setting)

    def get(self, key: str) -> Setting:
        return self.database_handler.read_setting(key)

    def delete(self, key: str):
        return self.database_handler.delete_setting(key)

    def contains(self, key: str) -> bool:
        try:
            self.database_handler.read_setting(key)
            return True
        except KeyError:
            return False