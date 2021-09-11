import json
import logging
import os


class FuturesConfig:
    def __init__(self, filePath: str):
        """
        Initialises the class to load from the given filePath
        :param filePath: Path to config file
        """
        self.file_path = filePath
        self.modified_time = 0
        self.data = []

    def load(self, smart_load: bool = True):
        """
        Loads the latest futures config.
        In Smart Load Mode (default) then file load will only
        take place if modified time has changed
        :param smart_load: True - only loads if modified time has changed since last load, False - Will always load
        (default - True)
        """
        # get the file time currently
        file_time_current = os.stat(self.file_path).st_mtime

        if file_time_current != self.modified_time or not smart_load:
            # the file time has changed since we last loaded so load again
            # load futures config
            logging.info(f'{self.file_path} has changed. Reloading ...')
            with open(self.file_path) as f:
                self.data = json.load(f)
                self.modified_time = os.stat(self.file_path).st_mtime
                logging.info(f'{self.file_path} loaded')
