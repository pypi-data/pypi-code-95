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


class Profile:
    def __init__(self) -> None:
        self.database_credentials = {}
        for key in ["hostname", "username", "password", "database"]:
            self.database_credentials.setdefault(
                key, "Please provide database information through Profile::set::methods"
            )

    def set_db_hostname(self, value):
        self.database_credentials["hostname"] = value

    def set_db_username(self, value):
        self.database_credentials["username"] = value

    def set_db_password(self, value):
        self.database_credentials["password"] = value

    def set_db_database(self, value):
        self.database_credentials["database"] = value
