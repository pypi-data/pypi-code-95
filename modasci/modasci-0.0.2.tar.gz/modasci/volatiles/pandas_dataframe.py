import pandas as pd

from .base import Volatile


class PandasDataFrame(Volatile):
    """Volatile proxy for pandas dataframes.

    This class can work in conjunction with: `Reference`.
    """

    def populate(self, gateway):
        self.values, self.ready = pd.read_csv(gateway, **self.importParameters), True

    def mutate(self, gateway, dataframe):
        dataframe.to_csv(gateway, **self.exportParameters)

    def toDict(self):
        return {
            'spec': 'PandasDataFrame',
            'importParameters': self.importParameters,
            'exportParameters': self.exportParameters,
        }
