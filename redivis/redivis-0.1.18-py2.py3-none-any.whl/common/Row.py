import json


class Row:
    def __init__(self, cells, variables=[]):
        self.cells = cells
        self.variables = variables

    def __getitem__(self, key):
        return self.cells[key]

    def __str__(self):
        return json.dumps(self.cells, indent=2)
