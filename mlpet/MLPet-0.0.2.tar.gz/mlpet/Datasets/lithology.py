import os
import joblib
import numpy as np
import pandas as pd
import importlib
import operator
from random import sample

import sklearn.preprocessing
#FIXME! This estimator is still experimental for now. To use it, you need to explicitly import enable_iterative_imputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, IterativeImputer

from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIError

from mlpet.Datasets import Dataset

class Lithologydata(Dataset):
    """    
    Subclass of ml_petrophysics.datasets

    shares all attributes and methods with the parent class as far as the user is concerned
    
    """
    def _load_lithology_data(self, client:CogniteClient, nan_threshold:float=-999.0):
        lithology_heads = client.sequences.list(metadata={'Subtype': 'FORCELithologyPrediction'}, limit=None)
        data = []
        for lithology_head in lithology_heads:
            lithology_training_data = client.sequences.data.retrieve_dataframe(id=lithology_head.id, start=None, end=None)
            lithology_training_data['well_name'] = lithology_head.metadata['wellbore']
            data.append(lithology_training_data)
        df = pd.concat(data)
        # remove small negative values
        for col in df.dtypes[df.dtypes != np.object].index:
            df[col].values[df[col]<=nan_threshold] = np.NaN        
        return df

    def _load_data_faster(self, cognite_client, reload=False):
        if reload:
            df = self._load_lithology_data(cognite_client)
        else:
            try:
                df = pd.read_pickle(self.data_path)
            except:
                df = self._load_lithology_data(cognite_client)
                df.to_pickle(self.data_path)
                print('Data saved in {}'.format(self.data_path))
        return df
        
