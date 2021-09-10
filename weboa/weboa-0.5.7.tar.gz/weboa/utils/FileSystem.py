from weboa import os
from weboa.utils import Printer


class filesystem:
    @staticmethod
    def is_file_changed(_weboa, i, precss="less"):
        if precss not in _weboa.keys():
            _weboa[precss] = dict()
        if i not in _weboa[precss].keys():
            _weboa[precss][i] = 0

        ts0 = _weboa[precss][i]
        ts1 = os.stat(i).st_mtime

        result = ts0 != ts1
        if(result):
            Printer.log(f"Compile {precss}")

        return result