# Allows nested asyncio event loop.
# This library depends on completing tasks on asyncio event loop, which
# will create a problem if the environment, such as web servers,
# GUI applications, Jupyter notebooks, etc, is already running an event loop.
# Using nest_asyncio below fixes this problem.
import nest_asyncio
nest_asyncio.apply()

from .Broker import Broker
from .Strategy import Strategy
from .Bot import Bot
from .Notifier import Notifier, addMessage
from .Data import Data
from .KrakenData import KrakenData
from .CSVData import CSVData
from .BacktestBroker import BacktestBroker
from .LNMBroker import LNMBroker
