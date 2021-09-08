import toml
from pathlib import Path


path_to_config = (Path(__file__) / '../config.toml').resolve()
_config = toml.load(path_to_config)

firebase = _config['firebase']
forecastflow = _config['forecastflow']
