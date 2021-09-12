import os
import yaml
import warnings
import joblib
import numpy as np
import pandas as pd
import random
import importlib
import operator
import warnings

from cognite.client import CogniteClient

from sklearn.experimental import enable_iterative_imputer # necessary for iterative imputer
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import BayesianRidge
import sklearn.preprocessing

class Dataset(object):
    """    
    The main class representing a dataset

    Attributes
    ----------
        settings: dict
            the required keys for the dictionary:
                'type': which subclass the settings belong to (required for the high-level API only and needs to follow a specific format),
                'file_name': pickled filename (not the full path) to read the data from, or dump the data to,
                'curves': list of features from the raw data to use,
                'id_column': name of the id column,
                'label_column': name of the column containing the labels,
                'num_filler': filler value for numerical curves(existing or wishing value for replacing missing values),
                'cat_filler': filler value categorical curves(existing or wishing value for replacing missing values),
                'scaler_method': (options: 'StandardScaler', 'RobustScaler'),
                'gradient_features': whether to calculate gradients of features (boolean),
                'window_features': whether to calculate rolling aggregations (min, max, mean) of features (boolean),
                'window': size of the rolling window for calculating the window features (int),
                'log_features': whether to add log of every feature as a new feature (boolean)
        *all setting keys are also set as class attributes

        folder_path: the path to the local copy of the data as well as the serialized scaler and imputer(if applicable)

    Methods
    -------
        load_from_cdf(client:CogniteClient, reload:bool)
            - loads data from CDF and dumps it in folder_path/file_name if reload=True
            - loads data from folder_path/file_name if reload=False
            - populates the 'df_original' attribute

        load_from_csv(filepath:str)
            - loads local data from filepath into the 'df_original' attribute

        load_from_pickle(filepath:str)
            - loads local data from filepath into the 'df_original' attribute

        load_from_dict(filepath:str)
            - loads local data from filepath into the 'df_original' attribute

        preprocess(train:bool)
            - performs all preprocessing according to the settings
            - splits data into train and test set (if train=True)
            - saves scaler and imputer to folder_path/scaler.joblib and folder_path/imputer.joblib (if applicable)
                or loads them from the mentioned paths to use for preprocessing
    """

    def __init__(self, mappings, settings, folder_path):

        def _ingest_input(att_name, att_val):
            if isinstance(att_val, dict):
                setattr(self, att_name, att_val)
            elif isinstance(att_val, str):
                if os.path.isfile(att_val):
                    att_path = '{}_path'.format(att_name)
                    setattr(self, att_path, att_val)
                    with open(getattr(self, att_path)) as file:
                        setattr(self, att_name, yaml.load(file, Loader=yaml.FullLoader))

        self.folder_path = folder_path
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

        _ingest_input(att_name='settings', att_val=settings)
        for key, val in self.settings.items():
            setattr(self, key, val)

        _ingest_input(att_name="mappings", att_val=mappings)
        if 'curve_mappings' in self.mappings.keys():
            self.curve_mappings = self.mappings['curve_mappings']
        if 'formations_map' in self.mappings.keys():
            self.formations_map = self.mappings['formations_map']
        if 'groups_map' in self.mappings.keys():
            self.groups_map = self.mappings['groups_map']

        # Fill in any possible gaps in settings
        if not hasattr(self, 'curves_to_scale'):
            setattr(self, 'curves_to_scale', [])

        if not hasattr(self, 'lognames'):
            setattr(self, 'lognames', [])
        
        if not hasattr(self, 'log_features'):
            setattr(self, 'log_features', [])

        if not hasattr(self, 'gradient_features'):
            setattr(self, 'gradient_features', [])

        if not hasattr(self, 'window'):
            self.window = 1

        if not hasattr(self, 'noise_removal_window'):
            self.noise_removal_window = None

        if not hasattr(self, 'feat_eng'):
            self.feat_eng = None
        
        if not hasattr(self, 'drop_original_curves'):
            self.drop_original_curves = False

        if not hasattr(self, 'scaler_method'):
            self.scaler_method = 'RobustScaler'

        if not hasattr(self, 'num_filler'):
            self.num_filler = 0

        if not hasattr(self, 'cat_filler'):
            self.cat_filler = 'MISSING'

        if not hasattr(self, 'curves_to_normalize'):
            warnings.warn('"curves_to_normalize" not provided in dataset settings, but GR will be normalized by default.')
            self.curves_to_normalize = ['GR']
        else:
            # GR must always be normalized
            if 'GR' not in self.curves_to_normalize:
                warnings.warn('GR added to "curves_to_normalize".')
                self.curves_to_normalize = self.curves_to_normalize + ['GR']

        # Standardize the provided curve names
        for attr in ['curves', 'curves_to_scale', 'curves_to_normalize', 'gradient_features', 'log_features']:
            setattr(self, '{}_original'.format(attr), getattr(self, attr))
            setattr(self, attr, self._standardize_names(getattr(self, attr)))

        # Check that the label curve is not present in the curves
        if self.label_column in self.curves:
            raise ValueError (f'Label column ({self.label_column}) is present in the input curves.')

        # Check that curves_to_scale is a  subset of curves
        for attr in ['curves_to_scale']:
            all_curves = set(getattr(self, 'curves'))
            sub_curves = set(getattr(self, attr))
            if not sub_curves.issubset(all_curves): 
                raise ValueError ('{} is not a subset of curves {}'.format(attr, getattr(self, 'curves')))

        if hasattr(self, 'imputer'):
            self.imputer_path = os.path.join(self.folder_path, 'imputer.joblib')
        else:
            self.imputer = None

        self.scaler_path = os.path.join(self.folder_path, 'scaler.joblib')
        self.data_path   = os.path.join(self.folder_path, self.file_name)

    def _feature_engineer(self, df):
        """
        Creates features the user specifies from features of the original dataset. If the value of the feature is 1,
        it will be added to curves to scale.

        Args:
            df (pd.DataFrame): dataframe to which add features from and to

        Returns:
            pd.DataFrame: dataframe with added features
        """
        if ('VPVS' in self.feat_eng.keys()):
            if (set(['AC', 'ACS']).issubset(set(df.columns))):
                df.loc[:, 'VPVS'] = df['ACS']*df['AC']
                if 'VPVS' not in self.curves:
                    self.curves.append('VPVS')
                if self.feat_eng['VPVS']==1:
                    self.curves_to_scale.append('VPVS')
            else:
                raise ValueError('Not possible to generate VPVS as both necessary curves (AC and ACS) are not present in dataset.')
            
        if ('RAVG' in self.feat_eng.keys()):
            r_curves = [c for c in ['RDEP', 'RMED', 'RSHA'] if c in df.columns]
            if len(r_curves)>1:
                df.loc[:, 'RAVG'] = df[r_curves].mean(axis=1)
                if 'RAVG' not in self.curves:
                    self.curves.append('RAVG')
                if self.feat_eng['RAVG']==1:
                    self.curves_to_scale.append('RAVG')
            else:
                raise ValueError('Not possible to generate RAVG as there is only one or none resistivities curves in dataset.')
            
        if 'LFI' in self.feat_eng.keys():
            if (set(['NEU', 'DEN']).issubset(set(df.columns))):
                df.loc[:, 'LFI'] = 2.95-((df['NEU']+0.15)/0.6)- df['DEN']
                df.loc[df['LFI']<-0.9,'LFI'] = 0
                df['LFI'] = df['LFI'].fillna(0)
                if 'LFI' not in self.curves:
                    self.curves.append('LFI')
                if self.feat_eng['LFI']==1:
                    self.curves_to_scale.append('LFI')
            else:
                raise ValueError('Not possible to generate LFI as NEU and/or DEN are not present in dataset.')
    
        if 'FI' in self.feat_eng.keys():
            if 'LFI' in df.columns:
                df.loc[:, 'FI'] = (abs(df['LFI'])+df['LFI'])/2
            elif (set(['NEU', 'DEN']).issubset(set(df.columns))):
                df.loc[:, 'LFI'] = 2.95-((df['NEU']+0.15)/0.6)- df['DEN']
                df.loc[df['LFI']<-0.9,'LFI']=0
                df.loc[:, 'LFI'] = df['LFI'].fillna(0)
                df.loc[:, 'FI']  = (abs(df['LFI'])+df['LFI'])/2
            else:
                raise ValueError('Not possible to generate FI as NEU and/or DEN are not present in dataset.')
            if 'FI' not in self.curves:
                self.curves.append('FI')
            if self.feat_eng['FI']==1:
                self.curves_to_scale.append('FI')

        if 'LI' in self.feat_eng.keys():
            if 'LFI' in df.columns:
                df.loc[:, 'LI']=abs(abs(df['LFI'])-df['LFI'])/2 
            elif (set(['NEU', 'DEN']).issubset(set(df.columns))):
                df.loc[:, 'LFI'] = 2.95-((df['NEU']+0.15)/0.6)- df['DEN']
                df.loc[df['LFI']<-0.9,'LFI']=0
                df.loc[:, 'LFI'] = df['LFI'].fillna(0)
                df.loc[:, 'LI']  = abs(abs(df['LFI'])-df['LFI'])/2 
            else:
                raise ValueError('Not possible to generate LI as NEU and/or DEN are not present in dataset.')
            if 'LI' not in self.curves:
                self.curves.append('LI')
            if self.feat_eng['LI']==1:
                    self.curves_to_scale.append('LI')

        if ('AI' in self.feat_eng.keys()):
            if (set(['DEN', 'AC']).issubset(set(df.columns))):
                df.loc[:, 'AI'] = df['DEN']*((304.8/df['AC'])**2)
                if 'AI' not in self.curves:
                    self.curves.append('AI')
                if self.feat_eng['AI']==1:
                    self.curves_to_scale.append('AI')
            else:
                raise ValueError('Not possible to generate AI as DEN and/or VP are not present in the dataset.')
    
        return df

    def _validate_data(self):
        """
        Checks that the data loaded into the Dataset includes the expected curves
        """
        # check that all expected curves are present in the data
        expected_curves = self.curves_original
        present_curves  = self.df_original.columns.tolist()
        expected_but_missing_curves = [c for c in expected_curves if c not in present_curves]
        if expected_but_missing_curves:
            warnings.warn("Warning...........There are curves that are expected but missing from data. They are being filled with num_filler {}".format(expected_but_missing_curves))
            self.df_original[expected_but_missing_curves] = self.num_filler

    def _make_col_dtype_lists(self, df):
        """
        Returns lists of numerical and categorical columns

        Args:
            df (pd.DataFrame): dataframe with columns to classify

        Returns:
            tuple: lists of numerical and categorical columns
        """
        num_cols = set(df._get_numeric_data().columns)
        cat_cols = list(set(df.columns) - set(num_cols))
        return list(num_cols), cat_cols

    def _read_data(self):
        """
        Identify column type and checks all expected curves are present
        """
        self._validate_data()

    def load_from_cdf(self, client:CogniteClient, reload=False):
        """                
        Loads and validates data
        
        Args:
            client: CogniteClient for authentication
            reload: boolean - default False
                if reload is True: downloads data from CDF as a pandas DataFrame and saves model_path/file_name as in Dataset settings
                if reload is False: expects pickled file to exist at model_path/file_name, otherwise loads it from CDF
        """
        self.df_original = self._load_data_faster(client, reload=reload)
        self._read_data()

    def load_from_csv(self, filepath, **kwargs):
        """
        Loads data from csv files and validates data

        Args:
            filepath (string): path to csv file
        """
        self.df_original = pd.read_csv(filepath, **kwargs)
        self._read_data()

    def load_from_pickle(self, filepath, **kwargs):
        """
        Loads data from pickle file and validates

        Args:       
            filepath (string): path to pickle file
        """
        self.df_original = pd.read_pickle(filepath, **kwargs)
        self._read_data()

    def load_from_dict(self, data_dict):
        """
        Loads data from a dictionary and validates it

        Args:
            data_dict (string): dictionary with data
        """
        self.df_original = pd.DataFrame.from_dict(data_dict)
        self._read_data()

    def load_from_df(self, data_df):
        """
        Loads data from dataframe and validates it

        Args:
            data_df (pandas.Dataframe): dataframe with data
        """
        self.df_original = data_df
        self._read_data()
    
    def _standardize_names(self, names, mapper=None):
        """
        Standardize curve names in a list based on the curve_mappings dictionary. 
        Any columns not in the dictionary are ignored.

        Args:
            names (list): list with curves names
            mapper (dictionary): dictionary with mappings. Defaults to curve_mappings.

        Returns:
            list: list of strings with standardized curve names
        """
        if mapper is None:
            mapper = self.curve_mappings
        standardized_names = []
        for name in names:
            if mapper.get(name):
                standardized_names.append(mapper.get(name))
            else:
                standardized_names.append(name)
        return standardized_names

    def _standardize_curve_names(self, df, mapper=None):
        """
        Standardize curve names in a dataframe based on the curve_mappings dictionary. 
        Any columns not in the dictionary are ignored. 

        Args:
            df (pd.DataFrame): dataframe to which apply standardization of columns names
            mapper (dictionary): dictionary with mappings. Defaults to curve_mappings.

        Returns:
            pd.DataFrame: dataframe with columns names standardized
        """
        if mapper is None:
            mapper = self.curve_mappings
        return df.rename(columns=mapper)

    def _encode_columns(self, df, columns=None):
        """
        Encodes categorical columns. Only available for certain categorical values at the moment.

        Args:
            df (pd.DataFrame): dataframe to which apply encoding of categorical variables
            columns (list): which columns to encode. Deafults to None.
        
        Returns:
            pd.DataFrame: dataframe with categorical columns encoded
        """   
        if columns is None:
            columns = self.cat_columns
        if 'FORMATION' in columns:
            df['FORMATION'] = df['FORMATION'].map(self.formations_map)
        if 'GROUP' in columns:
            df['GROUP'] = df['GROUP'].map(self.groups_map)
        if 'lsuName' in columns:
            df['lsuName'] = df['lsuName'].map(self.groups_map)

        return df

    def _split_df_wells(self, df, test_size):
        """
        Splits wells into two groups (train and val/test)

        Args:
            df (pd.DataFrame): dataframe with data of wells and well ID
            test_size (float): percentage (0-1) of wells to be in val/test data

        Returns:
            wells (list): wells IDs
            test_wells (list): wells IDs of val/test data
            training_wells (list): wells IDs of training data
        """
        wells          = df[self.id_column].unique()
        test_wells     = random.sample(list(wells), int(len(wells)*test_size))
        training_wells = [x for x in wells if x not in test_wells]
        return wells, test_wells, training_wells

    def _df_split_train_test(self, df, test_size=0.2, test_wells=None):
        """
        Splits dataframe into two groups: train and val/test set.

        Args:
            df (pd.Dataframe): dataframe to split
            test_size (float, optional): size of val/test data. Defaults to 0.2.
            test_wells (list, optional): list of wells to be in val/test data. Defaults to None.

        Returns:
            tuple: dataframes for train and test sets, and list of test wells IDs
        """
        if test_wells is None:
            test_wells = self._split_df_wells(df, test_size)[1]
        df_test  = df.loc[df[self.id_column].isin(test_wells)]
        df_train = df.loc[~df[self.id_column].isin(test_wells)]
        return df_train, df_test, test_wells

    def _filter_curves(self, df, curves=None):
        """
        Returns a dataframe with only curves chosen by user, filtered from the original dataframe

        Args:
            df (pd.DataFrame): dataframe to filter
            curves (list, optional): which curves should be kept. Defaults to None.

        Returns:
            pd.DataFrame: dataframe with relevant curves
        """
        if curves is None:
            curves = self.curves
        try:
            curves_to_keep = self.curves + [self.label_column] 
            if not self.id_column in curves_to_keep:
                curves_to_keep = curves_to_keep + [self.id_column]
            return df.loc[:, curves_to_keep]
        except KeyError:
            return df.loc[:, self.curves]

    def _normalize(self, col, ref_low, ref_high, well_low, well_high):
        """
        Formula to normalize min and max values to the key well's min and max values.

        Args:
            col (pd.Series): column from dataframe to normalize (series)
            ref_low (float): min value of the column of the well of reference
            ref_high (float): max value of the column of the well of reference
            well_low (float): min value of the column of well to normalize
            well_high (float): max value of the column of well to normalize

        Returns:
            pd.Series: normalized series
        """
        diff_ref  = ref_high - ref_low
        diff_well = well_high - well_low
        return ref_low + diff_ref*(col - well_low)/diff_well

    def _normalize_curves(self, df, **kwargs):
        """
        Normalizes dataframe columns.
        We choose one well to be a "key well" and normalize all other wells to its low and high values.
        If the user provides key wells, keys wells calculation is not perfomed.

        Args:
            df (pd.DataFrame): dataframe with columns to normalize

        Returns:
            tuple: pd.DataFrame with normalized values and dictionary with key wells and values
        """
        low_perc       = kwargs.get('low_perc', 0.05)
        high_perc      = kwargs.get('high_perc', 0.95)
        user_key_wells = kwargs.get('key_wells')
        save_key_wells = kwargs.get('save_key_wells', False)
        
        if user_key_wells is None:
            wells_data = df.groupby(self.id_column)
            key_wells  = {c: None for c in self.curves_to_normalize}
            for c in self.curves_to_normalize:
                low_p  = wells_data[c].quantile(low_perc)
                high_p = wells_data[c].quantile(high_perc)

                # get the key well with largest difference between limit values
                key_well = (high_p-low_p).idxmax()

                df.loc[:, 'low_p']  = df[self.id_column].map(low_p)
                df.loc[:, 'high_p'] = df[self.id_column].map(high_p)
                # save the key wells for normalization
                key_wells[c] = {
                    'curve': c,
                    'well_name': key_well,
                    'ref_low': df[df[self.id_column]==key_well]['low_p'].unique()[0],
                    'ref_high': df[df[self.id_column]==key_well]['high_p'].unique()[0]
                }
                # normalize all other wells
                df.loc[:, c] = df.apply(
                    lambda x: self._normalize(
                        x[c],
                        key_wells[c]['ref_low'],
                        key_wells[c]['ref_high'],
                        x['low_p'],
                        x['high_p'],
                        ),
                        axis=1
                        )
        else:
            # if key wells is provided as a dict with the same format
            if isinstance(user_key_wells, dict):
                if user_key_wells.keys() != set(self.curves_to_normalize):
                    raise ValueError(
                        "Curves included in the key wells dictionary incosistent with curves_to_normalize", 
                        user_key_wells.key(), self.curves_to_normalize)
                else:
                    key_wells = user_key_wells
                    for c in self.curves_to_normalize:
                        df.loc[:, 'low_p']  = key_wells[c]['ref_low']
                        df.loc[:, 'high_p'] = key_wells[c]['ref_high']
                        # normalize all other wells
                        df.loc[:, c] = df.apply(
                            lambda x: self._normalize(
                                x[c],
                                key_wells[c]['ref_low'],
                                key_wells[c]['ref_high'],
                                x['low_p'],
                                x['high_p'],
                                ),
                                axis=1
                                )
            else:
                ValueError("Other methods to provide key wells are not implemented yet!") 
        
        if save_key_wells:                          
            # save key wells to where model is
            joblib.dump(key_wells, os.path.join(self.folder_path, 'key_wells.joblib'))
        return df, key_wells

    def _preprocess(self, df, **kwargs):
        """
        Preprocessing pipeline for all wells, independently of well ID

        Args:
            df (pd.DataFrame): dataframe to preprocess

        Returns:
            tuple: preprocessed dataframe and columns that were added, if any
        """
        # filter relevant curves
        df = self._filter_curves(df)
        # add features
        added_cols = []
        # add_inter curves
        if set(['CALI', 'BS']).issubset(set(self.curves)):
            df, diff_cols = self._add_inter_curves(df, curves=['CALI', 'BS'], method='sub')
            added_cols    = added_cols + diff_cols
        # add feature log10
        if len(self.log_features)>0:
            df, log_cols = self._add_log_features(df)
            added_cols   = added_cols + log_cols
        return df, added_cols

    def _add_inter_curves(self, df, curves, method='sub'):
        """
        Creates a feature given by a calculation between two curves

        Args:
            df (pd.DataFrame): dataframe with curves to calculate another curve from
            curves (list): strings list with curves names
            method (string, optional): which computation to do between the two curves. Defaults to 'sub'.

        Returns:
            tuple: pd.DataFrame with new column and new column name
        """
        cls_name = method
        try:
            cls = getattr(operator, cls_name)
        except AttributeError as ae:
            print(ae)
        op_cols = ['{}_{}_{}'.format(curves[0], method, curves[1])]
        df.loc[:, op_cols[0]] = cls(df[curves[0]], df[curves[1]])
        return df, op_cols

    def _add_log_features(self, df):
        """
        Creates columns with log10 of curves

        Args:
            df (pd.DataFrame): dataframe with columns to calculate log10 from

        Returns:
            tuple: pd.DataFrame of new dataframe and list of names of new columns of log10
        """
        log_cols = [col+'_log' for col in self.log_features]
        for col in self.log_features:
            df_tmp = df[col].copy()
            df_tmp = df_tmp.clip(lower=0)
            df.loc[:, col+'_log'] = np.log10(df_tmp + 1)
        return df, log_cols

    def _add_gradient_features(self, df):
        """
        Creates columns with gradient of curves

        Args:
            df (pd.DataFrame): dataframe with columns to calculate gradient from

        Returns:
            tuple: pd.DataFrame of new dataframe and list of names of new columns of gradient
        """
        gradient_cols = [col+'_gradient' for col in self.gradient_features]
        for col in self.gradient_features:
            df.loc[:, col+'_gradient'] = np.gradient(df[col])
        return df, gradient_cols

    def _add_rolling_features(self, df, columns=None):
        """
        Creates columns with window/rolling features of curves

        Args:
            df (pd.DataFrame): dataframe with columns to calculate rolling features from
            columns (list, optional): columns to apply rolling features to. Defaults to None.

        Returns:
            tuple: pd.DataFrame of new dataframe and list of names of new columns of rolling features
        """
        if columns is None:
            columns, _ = self._make_col_dtype_lists(df[self.curves])
        mean_cols = [col+'_window_mean' for col in columns]
        min_cols  = [col+'_window_min' for col in columns]
        max_cols  = [col+'_window_max' for col in columns]
        for col in columns:
            df.loc[:, col+'_window_mean'] = df[col].rolling(center=False, window=self.window, min_periods=1).mean()
            df.loc[:, col+'_window_max']  = df[col].rolling(center=False, window=self.window, min_periods=1).max()
            df.loc[:, col+'_window_min']  = df[col].rolling(center=False, window=self.window, min_periods=1).min()
        window_cols = mean_cols + min_cols + max_cols
        return df, window_cols

    def _add_time_features(self, df, n):
        """
        Adds n past values of columns (for sequential models modelling).
        df (pandas.dataframe): dataframe to add time features to
        n (int): number of past values to include

        Args:
            df (pd.DataFrame): dataframe to add time features to
            n (int): number of time steps

        Returns:
            tuple: dataframe with added time feature columns and names of new columns
        """
        new_df = df.copy()
        cols   = [c for c in df.columns if c != self.id_column and c != self.label_column]
        all_time_cols = []
        for time_feat in range(1, n+1):
            time_cols = [f'{c}_{time_feat}' for c in cols]
            all_time_cols.append(time_cols)
            new_df[:, time_cols] = df[cols].shift(periods=time_feat)
        return new_df, sum(all_time_cols, [])

    def _scale_columns(self, df, columns, scaler_method='RobustScaler', **kwargs):
        """
        Scales specified columns

        Args:
            df (pd.DataFrame): dataframe containing columns to scale
            columns (list): list with columns to scale
            scaler_method (str, optional): scaling method. Defaults to 'RobustScaler'.

        Returns:
            pd.DataFrame: scaled columns
        """
        cls_name = scaler_method
        try:
            cls = getattr(sklearn.preprocessing, cls_name)
        except AttributeError as ae:
            print(ae)
        self.scaler = cls(**kwargs.get('scaler', {}))
        self.scaler.fit(df[columns])
        # save scaler to same path as model
        scaler_path = os.path.join(self.folder_path, 'scaler.joblib')
        joblib.dump(self.scaler, scaler_path)
        return self.scaler.transform(df[columns])

    def _iterative_impute(self, df, imputer=None):
        """
        Imputes missing values in specified columns with iterative imputer

        Args:
            df (pd.DataFrame): dataframe with columns to impute
            imputer (str, optional): imputer method. Defaults to None.

        Returns:
            pd.DataFrame: dataframe with imputed values
        """
        num_cols, _ = self._make_col_dtype_lists(df)
        # Iterative imputer at 
        missing_fractions = df[num_cols].isnull().sum()/df.shape[0]
        partially_missing_features = missing_fractions.loc[missing_fractions.values!=1].index.tolist()
        if 'DEPTH' in partially_missing_features:
            partially_missing_features.remove('DEPTH')
        if imputer is None:
            imputer = IterativeImputer(estimator=BayesianRidge())
            imputer.fit(df[partially_missing_features])
        else:
            warnings.warn("Providing an imputer is not implemented yet!")
        df.loc[:, partially_missing_features] = pd.DataFrame(
            imputer.transform(df[partially_missing_features]), 
            columns=partially_missing_features
        )    
        return df

    def _simple_impute(self, df):
        """
        Imputes missing values in specified columns with simple imputer

        Args:
            df (pd.DataFrame): dataframe with columns to impute

        Returns:
            pd.DataFrame: dataframe with imputed values
        """
        num_cols, cat_cols = self._make_col_dtype_lists(df)

        # Impute numerical columns
        missing_fractions_num          = df[num_cols].isnull().sum()/df.shape[0]
        partially_missing_features_num = missing_fractions_num.loc[missing_fractions_num.values!=1].index.tolist()
        if 'DEPTH' in partially_missing_features_num:
            partially_missing_features_num.remove('DEPTH')
        num_imputer = SimpleImputer(strategy='mean')
        num_imputer.fit(df[partially_missing_features_num])
        df.loc[:, partially_missing_features_num] = pd.DataFrame(
            num_imputer.transform(df[partially_missing_features_num]), 
            columns=partially_missing_features_num
        )    

        # Impute the categorical columns
        missing_fractions_cat          = df[cat_cols].isnull().sum()/df.shape[0]
        partially_missing_features_cat = missing_fractions_cat.loc[missing_fractions_cat.values!=1].index.tolist()
        cat_imputer                    = SimpleImputer(strategy='most_frequent')
        cat_imputer.fit(df[partially_missing_features_cat])
        df.loc[:, partially_missing_features_cat] = pd.DataFrame(
            cat_imputer.transform(df[partially_missing_features_cat]), 
            columns=partially_missing_features_cat
        )    

        return df

    def shuffle_dfs(self, x, y):
        """
        Returns dataframes shuffled equally in indices. Both dataframes should have same indices values.
        Useful for neural networks training for example.

        Args:
            x (pd.DataFrame): dataframe 1
            y (pd.DataFrame): dataframe 2

        Returns:
            tuple: both dataframes equally shuffled in indices
        """
        idx = np.random.permutation(x.index)
        return x.reindex(idx), y.reindex(idx)

    def generate_sequential_dataset(self, df, time_steps):
        """
        Returns the x (training) data in the format required by Keras LSTM/GRU models for LSTM networks

        Args:
            df (pd.DataFrame): data for input in LSTM networks (keras)
            time_steps (int): number of time steps

        Returns:
            np.array: samples with time steps included
        """
        samples = df.values
        if df.columns.size%(time_steps+1)==0: 
            n_original_cols = df.columns.size//(time_steps+1)
            samples         = samples.reshape((len(samples), time_steps+1, n_original_cols))
            return samples
        raise ValueError ('Number of columns not divisible by number of time steps.')

    def _process_well(self, df, **kwargs):
        """
        Process specific well: imputation, features creation (rolling, gradient)

        Args:
            df (pd.DataFrame): dataframe of one well

        Returns:
            tuple: processed dataframe of well, added columns names, curves to scale list
        """
        # impute features
        if self.imputer == 'iterative':
            df = self._iterative_impute(df)
        if self.imputer == 'simple':
            df = self._simple_impute(df)

        added_cols = []
        # add rolling features
        if self.window_features:
            df.loc[:, self.curves], window_cols = self._add_rolling_features(df)
            added_cols = added_cols + window_cols

        # add gradient features
        if self.gradient_features:
            df.loc[:, self.curves], gradient_cols = self._add_gradient_features(df)
            added_cols = added_cols + gradient_cols

        # add the created features to curves_to_scale, if the original ones are also in curves_to_scale,
        # including the logs that were generated for the whole data
        feats_to_add = []
        for col in self.curves_to_scale:
            feats_to_add = feats_to_add + [c for c in df.columns if col+'_' in c]
            
        # scale_features
        curves_to_scale = self.curves_to_scale + feats_to_add

        return df, added_cols, curves_to_scale

    def _remove_noise(self, df, cols):
        """
        Removes noise by applying a median filter in each curve

        Args:
            df (pd.DataFrame): dataframe to which apply median filtering
            cols (list): list of column to apply noise removal with median filter

        Returns:
            pd.DataFrame: dataframe after removing noise
        """
        cols     = [c for c in cols if c != 'DEPTH']
        df.loc[:, cols] = df[cols].rolling(
            self.noise_removal_window,
            center=True,
            min_periods=1
            ).median()
        return df

    def _drop_rows_wo_label(self, df, **kwargs):
        """
        Removes columns with missing targets.
        Now that the imputation is done via pd.df.fillna(), what we need is the constant filler_value
        If the imputation is everdone using one of sklearn.impute methods or a similar API, we can use 
        the indicator column (add_indicator=True)

        Args:
            df (pd.DataFrame): dataframe to process

        Returns:
            pd.DataFrame: processed dataframe
        """
        filler_value = kwargs.get('filler_value', None)
        if filler_value is not None:
            return df.loc[df[self.label_column]!=filler_value, :]
        else:
            return df.loc[~df[self.label_column].isna(), :]

    def _remove_cutoff_values(self, df, th=0.05):
        """
        Returns the dataframe after applying the cutoff for some curves

        Args:
            df (pd.DataFrame): dataframe to remove outliers
            th (float, optional): threshold of number of samples that are outliers. 
            Used for displaying warnings of too many samples removed. Defaults to 0.05.

        Returns:
            pd.DataFrame: dataframe without outliers
        """
        len_df = len(df)

        if 'GR' in self.curves:
            outliers_low  = df[df.GR<0]
            outliers_high = df[df.GR>250]
            if (len(outliers_low)+len(outliers_high))/len_df>th:
                warnings.warn("Warning...........GR has more than 5% of its values lower than 0 or higher than 250")
            df.loc[df.GR<0, 'GR']   = 0
            df.loc[df.GR>250, 'GR'] = 250
        
        for resistivity in ['RSHA', 'RMED', 'RDEP']:
            if resistivity in self.curves:
                outliers = df[df[resistivity]>100]
                if len(outliers)/len_df>th:
                    warnings.warn("Warning...........{} has more than 5% of its values higher than 100")
                df.loc[df[resistivity]>100, resistivity] = 100

        if 'NEU' in self.curves:
            outliers_high = df[df.NEU>1]
            outliers_low  = df[df.NEU<-0.5]
            df = df.drop(list(outliers_low.index) + list(outliers_high.index))
            if (len(outliers_low)+len(outliers_high))/len_df>th:
                warnings.warn("Warning...........NEU has more than 5% of its values higher than 1")
        
        if 'PEF' in self.curves:
            outliers = df[df.PEF>10]
            if len(outliers)/len_df>th:
                warnings.warn("Warning...........PEF has more than 5% of its values higher than 10")
            df = df.drop(outliers.index)

        return df
        
    def train_test_split(self, test_size=0.2, df=None, **kwargs):
        """
        Splits a dataset into training and val/test sets.
        **kwargs: test_size and test_wells (if applicable) 
        
        Args:
            test_size (float, optional): percentage of data to be test set. Defaults to 0.2.
            df (pd.DataFrame, optional): dataframe with data. Defaults to None.

        Returns:
            tuple: dataframes for train and test sets, and list of test wells IDs
        """
        if df is None:
            df = self.df_original
        df = self._drop_rows_wo_label(df, **kwargs)
        return self._df_split_train_test(df, test_size=test_size, **kwargs)

    def feature_target_split(self, df, **kwargs):
        """
        Splits set into features and target

        Args:
            df (pd.DataFrame): dataframe to be split

        Returns:
            tuple: input (features) and output (target) dataframes
        """
        df = self._standardize_curve_names(df, mapper=kwargs.get('curve_mappings', None))
        if self.id_column not in self.curves:
            X = df.loc[:, ~df.columns.isin([self.label_column, self.id_column])]
        else:
            X = df.loc[:, ~df.columns.isin([self.label_column])]
        y = df[self.label_column]
        return X, y

    def oversample_targets(self, df, method="RandomOverSampler"):
        """
        Oversamples dataset

        Args:
            df (pd.DataFrame): dataframe to oversample
            method (str, optional): method used for oversampling. Defaults to "RandomOverSampler".

        Returns:
            pd.DataFrame: oversampled dataframe
        """
        features                    = df.loc[:, df.columns != self.label_column]
        targets                     = df.loc[:, self.label_column]
        module_name                 = "imblearn.over_sampling"
        cls_name                    = method
        cls                         = getattr(importlib.import_module(module_name), cls_name)
        oversampler                 = cls()
        features, targets           = oversampler.fit_resample(features, targets)
        features[self.label_column] = targets
        return features
        
    def _apply_metadata(self, df, **kwargs):
        """
        Applies specified metadata to data

        Args:
            df (pd.DataFrame): dataframe to apply metadata to

        Returns:
            tuple: pd.Dataframe after applying metadata, list of numerical columns and list of categorical columns
        """
        num_cols, cat_cols = self._make_col_dtype_lists(df)
        imputed            = kwargs.get('imputed', False)
        if imputed:
            print('Applying metadata....')
            if 'num_filler' in kwargs.keys():
                num_filler = kwargs['num_filler']
                if imputed:
                    df.loc[:, num_cols] = df[num_cols].replace(to_replace=num_filler, value=np.nan)
            if 'cat_filler' in kwargs.keys():
                cat_filler = kwargs['cat_filler']
                if imputed:
                    df.loc[:, cat_cols] = df[cat_cols].replace(to_replace=cat_filler, value=np.nan)
        return df, num_cols, cat_cols 

    def preprocess(self, df, **kwargs):
        """
        Main preprocess function, including all required steps by the user

        Args:
            df (pd.Dataframe): dataframe to which apply preprocessing

        Returns:
            pd.Dataframe: preprocessed dataframe
            dictionary: key wells and values for each curve
            list: feats_to_keep specifies which curves should be kept in accordance to the settings file
        """
        
        # identify categorical and numerical curves, impute if needed
        df, num_cols, cat_cols = self._apply_metadata(df, **kwargs.get('_metadata', {}))
        # standardize curve names
        df = self._standardize_curve_names(df, mapper=kwargs.get('curve_mappings', None))
        # remove or clip values in some curves
        df = self._remove_cutoff_values(df)
        # remove noise if chosen
        if self.noise_removal_window is not None:
            df = self._remove_noise(df, cols=list(num_cols))
        # generate specified features if chosen
        if self.feat_eng is not None:
            df = self._feature_engineer(df)
        # normalize some curves 
        df, key_wells = self._normalize_curves(df, **kwargs.get('_normalize_curves', {}))
        # preprocess whole dataset (including add features to the dataset)
        df, added_cols = self._preprocess(df, **kwargs.get('_preprocess', {}))
        
        # preprocess some curves per well
        if self.id_column in df.columns:
            well_names = df[self.id_column].unique()
            res_df     = pd.DataFrame()
            time_cols  = None
            for well in well_names:
                well_df                            = df.loc[df[self.id_column]==well, :].copy()
                well_df, new_cols, curves_to_scale = self._process_well(well_df, **kwargs.get('_process_well', {}))
                if 'time_features' in kwargs.keys():
                    well_df, time_cols = self._add_time_features(well_df, kwargs['time_features'])
                res_df = res_df.append(well_df)
            df = res_df.copy()
            curves_to_scale = curves_to_scale + time_cols if time_cols!=None else curves_to_scale
        else:
            df, new_cols, curves_to_scale = self._process_well(df, **kwargs.get('_process_well', {}))
            warnings.warn('Not possible to process per well as well ID is not in dataset. Preprocessing was done considering all data is from the same well.')
        
        # fill the missing Z_LOC values with regards to DEPTH_MD(always present)
        if ("Z_LOC" in self.curves) and ("DEPTH_MD" in self.curves):
            df.loc[:, 'Z_LOC'] = df['Z_LOC'].fillna(-(df['DEPTH_MD'] - 20))
        # impute missing rows
        num_cols, cat_cols  = self._make_col_dtype_lists(df)
        df.loc[:, num_cols] = df[num_cols].fillna(self.num_filler)
        df.loc[:, cat_cols] = df[cat_cols].fillna(self.cat_filler)

        # map the categorical features
        df = self._encode_columns(df, columns=cat_cols)
        # drop original values if chosen otherwise all columns will be considered
        feats_to_keep = list(df.columns)
        if self.drop_original_curves:
            to_drop = self.log_features + self.gradient_features
            # we have to add here to drop the curves generated for time features from the original
            if 'time_features' in kwargs.keys():
                time_cols_drop = []
                for t in range(1, kwargs['time_features']+1):
                    time_cols_drop = time_cols_drop + [f'{c}_{t}' for c in to_drop]
                to_drop = to_drop + time_cols_drop
            feats_to_keep = [c for c in df.columns if c not in to_drop]
        

        # make sure we only have numerical features to scale
        num_feats       = set(df[feats_to_keep]._get_numeric_data().columns)
        curves_to_scale = list(set(curves_to_scale) & num_feats)
        # scale columns globally
        if len(curves_to_scale) > 0:
            df.loc[:, curves_to_scale] = self._scale_columns(
                df, 
                columns=curves_to_scale, 
                scaler_method=self.scaler_method, 
                **kwargs
            )      
        
        added_cols = added_cols + new_cols
        self.added_features = added_cols

        return df, key_wells, feats_to_keep