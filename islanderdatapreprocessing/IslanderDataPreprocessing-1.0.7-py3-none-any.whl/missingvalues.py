from .encoder2 import Encoder
import pandas as pd
from sklearn.impute import SimpleImputer
class MissingValues:
    def __init__(self, df):
        data = Encoder(df = df)
        data.Check()
        self.df = data.df

    def Check(self):
        self.isnull = []
        for i in self.df.columns:
            if (self.df[i].isnull().values.any()):
                self.isnull.append(i)
        if (len(self.isnull) >0):
            self.Imputer()
        return self.df
    def Imputer(self):
        imputer = SimpleImputer(strategy="median")
        new_data = imputer.fit_transform(self.df)
        convert = pd.DataFrame(new_data, columns=self.df.columns,index=self.df.index)
        self.df = convert