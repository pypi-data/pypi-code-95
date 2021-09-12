import os
import configparser

class TurbineConfiguration:
    def __init__(self) -> None:
        config_dir = os.path.join(os.path.expanduser("~"), ".turbineml")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        self.config_path = os.path.join(config_dir, "config")
        self._read_config()
    
    def _read_config(self):
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        if not "turbineml" in self.config:
            self.config.add_section("turbineml")
    
    def _write_config(self):
        with open(self.config_path, "w") as configfile:
            self.config.write(configfile)

    def get_api_key(self):
        if "TURBINE_API_KEY" in os.environ:
            return os.environ["TURBINE_API_KEY"]
        return self.config.get("turbineml", "api_key", fallback=None)
    
    def set_api_key(self, api_key):
        self._read_config()
        self.config.set("turbineml", "api_key", api_key)
        self._write_config()
    
    def get_api_url(self):
        if "TURBINE_API_ENDPOINT" in os.environ:
            return os.environ["TURBINE_API_ENDPOINT"]
        return "https://app.turbineml.com/api/"

_config = TurbineConfiguration()
