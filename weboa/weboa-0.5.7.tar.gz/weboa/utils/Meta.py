import json

from weboa import __VERSION__
from weboa.utils import Printer, Processing

class meta:

    @staticmethod
    def Weboa_Init():
        return {"version": __VERSION__}

    @staticmethod
    def Weboa_Open():
        try:
            with open(".weboa", "r") as f:
                wf = f.read()

            return json.loads(wf)
        except FileNotFoundError:
            Printer.error("Weboa project doesn't exist")
            return False

    @staticmethod
    def Weboa_Add(key, value):
        Printer.log(f"Weboa Add {value} to {key}")
        _weboa = Processing.Processing.Weboa_Open()
        if (_weboa):
            _weboa[key] = value
            Processing.Processing.Weboa_Save(_weboa)
            return True
        else:
            return False

    @staticmethod
    def Weboa_Save(fweboa):
        with open(".weboa", "w") as f:
            fweboa = json.dumps(fweboa)
            f.write(fweboa)