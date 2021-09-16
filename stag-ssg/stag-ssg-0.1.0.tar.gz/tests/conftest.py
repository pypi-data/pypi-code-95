import os
import sys

import pytest

from stag.config import Config
from stag.ecs import Site


sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def site(config):
    site = Site(config=config)
    return site
