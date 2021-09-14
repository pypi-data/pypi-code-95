"""FutureLog aims to record logs per category and then consume them on demand.

Useful to keep logging in order in async app.

Usage example: reporting of deployment on multiple servers.
"""

from futurelog.logger import FutureLogger
