from mlpet.Datasets import Dataset
from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIError
import re
import numpy as np
import pickle
import pandas as pd
import warnings
import math

def generate_log_settings(settings, lognames, badlognames, log_curves=None):
    all_settings = dict()
    for i, logname in enumerate(lognames):
        all_settings[logname] = settings
        all_settings[logname]['label_column'] = badlognames[i]
        if log_curves is not None:
            all_settings[logname]['curves'] = log_curves
    return all_settings

class Sheardata(Dataset):
    def __init__(self, mappings, settings, folder_path):
        """
        Initializes a Sheardata instance

        Args:
            settings (dict): dicitionary with settings
            folder_path (str): path to folder
        """
        super().__init__(mappings, settings, folder_path)

        if len(self.lognames)>0:
            attr = 'lognames'
            setattr(self, attr, self._standardize_names(getattr(self, attr)))
            self._validate_lognames()

    def _add_depth_label(self, client:CogniteClient, df):
        df['lsuName'] = "UNKNOWN"
        for well in df.well_name.unique():
            tops = client.sequences.list(metadata={'wellbore_name': well, 'type': "FormationTops"})
            if tops is None or len(tops) == 0:
                continue
            rows = tops[0].rows(start=None, end=None).to_pandas()
            rows = rows[rows.lsuLevel=='GROUP'].sort_values(['lsuTopDepth'])
            
            labels = []
            levels = []
            label  = "UNKNOWN"
            for index, row in rows.iterrows():
                new_label = row.lsuName

                if label == new_label or new_label == 'UNDEFINED GP': # merge levels
                    levels = levels[:-1]
                    levels.append(row.lsuBottomDepth)
                else:
                    label = new_label
                    labels.append(label)
                    levels.extend([row.lsuTopDepth, row.lsuBottomDepth])
            levels = list(dict.fromkeys(levels))
            labels = list(dict.fromkeys(labels))
            if len(levels) != len(labels) + 1:
                print("invalid formation top information")
                continue

            well_df = df[df.well_name==well]
            df.loc[df.well_name==well, 'lsuName'] = pd.cut(well_df.DEPTH, levels, labels=labels, include_lowest=True)
        return df

    def _load_shear_data(self, client:CogniteClient, clean_bad_values=False, include_depth_label=True):
        cpiCols          = ['DEPTH','PHIT','PHIT_SAND','PHIE','SW','SWT','SWT_SAND','VSH','VCL']
        shear_data_heads = client.sequences.list(metadata={'Subtype': 'ShearPredictionBenchmark'}, limit=None)
        data             = []
        for shear_data_head in shear_data_heads:
            shear_data              = client.sequences.data.retrieve_dataframe(id=shear_data_head.id, start=None, end=None)
            well_name               = shear_data_head.metadata['wellbore']
            shear_data['well_name'] = well_name           
            data.append(shear_data)
        df = pd.concat(data)
        
        # Merge DEPTH and DEPT
        if "DEPT" in shear_data.columns:
            df['DEPTH'] = np.where(df['DEPTH'].isna(), df['DEPT'], df['DEPTH'])
            df.drop(columns=["DEPT"], inplace=True)
        
        # Add lsuName label based on depth
        if include_depth_label:
            df = self._add_depth_label(client, df)
            
        return df

    def _load_data_faster(self, cognite_client, reload=False):
        if reload:
            df = self._load_shear_data(cognite_client)
        else:
            try:
                infile = open(self.data_path, 'rb')
                df     = pickle.load(infile)
                infile.close()
            except:
                df      = self._load_shear_data(cognite_client)
                outfile = open(self.data_path, 'wb')
                pickle.dump(df,outfile)
                outfile.close()
        return df

    def cpi_external_id(self, well_name):
        external_id = re.sub(r'[/\s]', '_', well_name)
        return f"{external_id}_CPI.las"
    
    def _add_custom_features(self, df):
        """
        Create features necessary for analysis

        Args:
            df (pd.DataFrame): dataframe with samples

        Returns:
            pd.DataFrame: dataframe with added features
        """
        df['VP']                      = 304.2/df['AC']
        df['VP2']                     = df['VP']**2
        df['LFI']                     = 0
        df['LFI']                     = 2.95 - ((df['NEU']+0.15)/0.6) - df['DEN']
        df.loc[df['LFI']<-0.9, 'LFI'] = 0
        df['LFI']                     = df['LFI'].fillna(0)
        df['FI']                      = (abs(df['LFI'])+df['LFI'])/2 
        df['LI']                      = abs(abs(df['LFI'])-df['LFI'])/2 
        self.added_features           = ['VP', 'VP2', 'LFI', 'FI', 'LI']
        return df

    def _validate_lognames(self):
        """
        Checks all necessary curves are included
        """
        if not 'ACS' in self.lognames:
            if 'ACS' in self.curves:
                warning_msg = "'ACS' is not used to determine bad samples in {}.".format(self.lognames)
                warnings.warn("Warning...........{}".format(warning_msg))
        if 'ACS' in self.lognames:
            if 'AC' not in self.curves:
                warning_msg = "'AC' is used to determine bad samples in 'ACS'. Without 'AC' some of the bad logs may be misslabeld as good."
                warnings.warn("Warning...........{}".format(warning_msg))
        if 'DEN' in self.lognames:
            if 'DENC' not in self.curves:
                warning_msg = "'DENC' is used to determine bad samples in 'DEN'. Without 'DENC' some of the bad logs may be misslabeld as good."
                warnings.warn("Warning...........{}".format(warning_msg))
            if 'CALI' not in self.curves:
                warning_msg = "'CALI' is used to determine bad samples in 'DEN'. Without 'CALI' some of the bad logs may be misslabeld as good."
                warnings.warn("Warning...........{}".format(warning_msg))
            if 'BS' not in self.curves:
                warning_msg = "'BS' is used to determine bad samples in 'DEN'. Without 'BS' some of the bad logs may be misslabeld as good."
                warnings.warn("Warning...........{}".format(warning_msg))                
        if 'DEPTH' not in self.curves:
            warning_msg = "'DEPTH' is used to determine bad samples. Without 'DEPTH' some of the bad logs may be misslabeld as good."
            warnings.warn("Warning...........{}".format(warning_msg))

    def _get_constant_derivatives(self, df):
        """
        Flags bad curves samples if derivatives within a window are constant

        Args:
            df (pd.DataFrame): dataframe with samples

        Returns:
            pd.DataFrame: dataframe with flagged bad curves values
        """
        for logname in self.lognames:
            df['{}_d1'.format(logname)] = np.gradient(df[logname], df['DEPTH'])
            df['{}_d2'.format(logname)] = np.gradient(df['{}_d1'.format(logname)], df['DEPTH'])
            df['{}_cnst_derivative'.format(logname)] = df['{}_d1'.format(logname)] == df['{}_d2'.format(logname)]
            df['bad_{}_rules'.format(logname)] = df[['bad_{}_rules'.format(logname), '{}_cnst_derivative'.format(logname)]].any(axis=1)
        return df

    def _get_constant_windows(self, df):
        """
        Flags bad curves samples if values within a window are constant

        Args:
            df (pd.DataFrame): dataframe with samples

        Returns:
            pd.DataFrame: dataframe with flagged bad curves values
        """
        for logname in self.lognames:
            df['{}_minw'.format(logname)]        = df[logname].rolling(self.window_size, min_periods=self.window_size).min()
            df['{}_maxw'.format(logname)]        = df[logname].rolling(self.window_size, min_periods=self.window_size).max()
            df['{}_cnst_window'.format(logname)] = df['{}_minw'.format(logname)] == df['{}_maxw'.format(logname)]
            df['bad_{}_rules'.format(logname)]   = df[['bad_{}_rules'.format(logname), '{}_cnst_window'.format(logname)]].any(axis=1)
        return df

    def _get_vpvs(self, df):
        """
        Flags bad ACS samples based on low VPVS values

        Args:
            df (pd.DataFrame): dataframe with samples

        Returns:
            pd.DataFrame: dataframe with flagged bad ACS
        """
        df['vpvs']          = df['ACS']/df['AC']
        df['low_vpvs']      = df['vpvs'] <= self.vpvs_threshold
        df['bad_ACS_rules'] = df[['bad_ACS_rules', 'low_vpvs']].any(axis=1)
        return df

    def _get_drho(self, df):
        """
        Flags bad DEN based on high DRHO values

        Args:
            df (pd.DataFrame): dataframe with samples

        Returns:
            pd.DataFrame: dataframe with flagged bad DEN
        """
        df['high_drho']     = df['DENC'] > self.drho_threshold
        df['bad_DEN_rules'] = df[['bad_DEN_rules', 'high_drho']].any(axis=1)
        return df
        
    def _get_cali_bs(self, df):
        """
        Flags bad DEN based on the size of CALI-BS 

        Args:
            df (pd.DataFrame): dataframe with samples

        Returns:
            pd.DataFrame: dataframe with flagged bad DEN
        """
        df['CALI_BS']       = df['CALI'] - df['BS']
        df['high_cali_bs']  = np.abs(df['CALI_BS']) > self.cali_bs_threshold
        df['bad_DEN_rules'] = df[['bad_DEN_rules', 'high_cali_bs']].any(axis=1)
        return df

    def mark_bad_samples(self, df, window_size=None, **kwargs):
        """
        Marks bad samples based on rules

        Args:
            df (pd.DataFrame): dataframe with data
            window_size (int, optional): size of intervals to process data. Defaults to None.

        Returns:
            pd.DataFrame: dataframe with bad samples flagged
        """
        self.drho_threshold    = kwargs.get('drho_threshold', 0.05)        
        self.cali_bs_threshold = kwargs.get('cali_bs_threshold', 1.5)        
        self.vpvs_threshold    = kwargs.get('vpvs_threshold', math.sqrt(2.))
        self.window_size       = kwargs.get('window_size', self.window)

        for logname in self.lognames:
            df['bad_{}_rules'.format(logname)] = np.where(df[logname].isnull(), 1, 0)

        df = self._get_constant_derivatives(df)
        df = self._get_constant_windows(df)
        if 'ACS' in self.lognames:
            if ('AC' in self.curves) and ('AC' in df.columns):
                df = self._get_vpvs(df)
        if 'DEN' in self.lognames:
            if ('DENC' in self.curves) and ('DENC' in df.columns):
                df = self._get_drho(df)
            if ('CALI' in self.curves) and ('CALI' in df.columns) and ('BS' in self.curves) and ('BS' in df.columns):
                df = self._get_cali_bs(df)
        return df

    def _filter_bad_logs(self, df, df_badlogs):
        """
        Removes bad log samples for the curves specified in "lognames" settings.
        df: dataframe with labeled data
        df_badlogs: dataframe with rule based badlogs data

        Args:
            df (pd.DataFrame): dataframe to remove bad logs samples (needs to be labeled)
            df_badlogs (pd.DataFrame): dataframe with rule based badlogs data

        Returns:
            pd.DataFrame: dataframe without badlogs samples
        """
        badlogs = []
        # perform an OR between labeled and rule- or model-based logs, and remove flagged as bad
        for name in self.lognames:
            idx = np.where((
                df_badlogs['BAD'+name].fillna(0).astype(bool) | 
                self.df_original['BAD'+name].fillna(0).astype(bool)
                )==True
            )
            badlogs += list(idx[0])
        df = df.drop(badlogs)
        return df

    def _preprocess(self, df, **kwargs):
        """
        Preprocessing pipeline for all wells, independently of well ID.
        Replaces _preprocess from inherited class adding a filter bad logs processing if that is labeled

        Args:
            df (pd.DataFrame): dataframe to preprocess

        Returns:
            tuple: preprocessed dataframe and columns that were added, if any
        """
        # global preprocess
        # filter away bad logs
        if len(self.lognames)>0:
            df = self._filter_bad_logs(df, self.mark_bad_samples(df))
        # filter relevant curves
        df = self._filter_curves(df)
        # add features
        added_cols = []
        
        # add_inter curves
        if set(['CALI', 'BS']).issubset(set(self.curves)):
            df, diff_cols = self._add_inter_curves(df, curves=['CALI', 'BS'], method='sub')
            added_cols = added_cols + diff_cols
        
        # add feature log
        if len(self.log_features)>0:
            df, log_cols = self._add_log_features(df)
            added_cols = added_cols + log_cols
        return df, added_cols