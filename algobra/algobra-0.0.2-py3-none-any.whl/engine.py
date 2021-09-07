import os
from collections import defaultdict

# **** profiler ****

DEBUG = os.getenv("DEBUG", None) is not None
if DEBUG:
    import atexit, time

    debug_counts, debug_times = defaultdict(int), defaultdict(float)

    def print_debug_exit():
        for name, _ in sorted(debug_times.items(), key=lambda x: -x[1]):
            print(f"{name:>20} : {debug_counts[name]:>6} {debug_times[name]:>10.2f} ms")

    atexit.register(print_debug_exit)


def default_db_access():
    return {
        "host": "localhost",
        "user": "sec_user",
        "passw": "password",
        "name": "securities_master",
    }


class Profile:
    def __init__(self) -> None:
        self.database_credentials = defaultdict(default_db_access)

    def say_hello(self):
        return "Hello"
