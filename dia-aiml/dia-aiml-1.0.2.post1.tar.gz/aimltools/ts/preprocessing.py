"""
Sub-module of TSAnalysis

Contains classes and methods to perform preprocessing on signal data
"""

import numpy as np
import pandas as pd
import logging
import random
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
from deprecation import deprecated

logger = logging.getLogger(__name__)


class DataPreparation:
    def __init__(self):
        self.__time_fld = 'vtime'
        self.__name_fld = 'vtag'
        self.__value_fld = 'vvalue'


    def setup_mappings(self, time_fld, name_fld, value_fld):
        self.__time_fld = time_fld
        self.__name_fld = name_fld
        self.__value_fld = value_fld


    def get_feature_matrix(self, df, feature_list):
        try:
            feat_df = df.pivot_table(index=self.__time_fld, columns=self.__name_fld, values=self.__value_fld)
            feat_df_cols = list(feat_df.columns)
            diff_cols = self.__get_diff(feature_list, feat_df_cols)
            missing_cols_df = pd.DataFrame(index=feat_df.index, columns=diff_cols)
            feat_df = pd.concat([feat_df, missing_cols_df], axis=1)
            feat_df = feat_df[feature_list]
            return feat_df
        except Exception as error:
            logger.info("Unable to create feature matrix :{}".format(error))
    
    # Fixing SHAP error, will be removed once entire project moves to new schema
    def get_feature_matrix_Old(self, df, feature_list):
        try:
            feat_df = df.pivot_table(index='event_time', columns='ft_name', values='nvalue')
            feat_df_cols = list(feat_df.columns)
            diff_cols = self.__get_diff(feature_list, feat_df_cols)
            missing_cols_df = pd.DataFrame(index=feat_df.index, columns=diff_cols)
            feat_df = pd.concat([feat_df, missing_cols_df], axis=1)
            feat_df = feat_df[feature_list]
            return feat_df
        except Exception as error:
            logger.info("Unable to create feature matrix :{}".format(error))
    
    def check_data_quality(self, df, feature_list, max_null_ratio):
        quality = False
        try:
            cycles = len(df[self.__time_fld].unique())
            existing_features = df[self.__name_fld].unique()
            feature_match1 = set(df[self.__name_fld].unique()).issubset(feature_list)
            feature_match2 = set(feature_list).issubset(df[self.__name_fld].unique())
            df_feat = self.get_feature_matrix(df, feature_list)
            attributr_nan_percentage = self.__get_naratio(df_feat, feature_list)
            null_flag = max(attributr_nan_percentage) < max_null_ratio
            null_validation = self.__validate(df_feat, feature_list, thr=max_null_ratio)

            if feature_match1 and feature_match2 and null_flag and null_validation:
                quality = True
            
            data_quality_report = {}
            data_quality_report['cycle count'] = cycles
            data_quality_report['data set contains all features'] = feature_match1 and feature_match2 
            data_quality_report['data set contains all features'] = feature_match2 
            data_quality_report['feature list'] = existing_features
            data_quality_report['null feature percentage'] = attributr_nan_percentage
            data_quality_report['quality pass'] = quality
            return [quality, data_quality_report]
        except Exception as error:
            logger.info("Unable to generate quality :{}".format(error))
            
    
    def normalize(self,df):
        try:
            scaler = MinMaxScaler()
            scaler.fit(df)
            return [scaler, scaler.transform(df)]
        except Exception as error:
            logger.info("Unable to Normalize data :{}".format(error))

            
    def fill_na(self,df):
        try:
            df_new = df.apply(lambda x: x.fillna(x.mean()), axis=0)
            return df_new
        except Exception as error:
            logger.info("Error in imputation :{}".format(error))

    
    def __get_diff(self, li1, li2):                                            # make private 
        return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

    
    def __get_naratio(self, df_feat, feature_list):
        try:
            nacounts = []
            for ftn in feature_list:
                nacounts.append(df_feat[ftn].isna().sum() / len(df_feat))
            return nacounts
        except Exception as error:
            logger.info("Error while calculating null values :{}".format(error))

            
    def __validate(self, df_feat, feature_list, thr = 0.4):
        try:
            nacounts = self.__get_naratio(df_feat, feature_list)
            for v in nacounts:
                if (v > thr):
                    return False
            return True
        except Exception as error:
            logger.info("Unable to validate :{}".format(error))

    
    @staticmethod
    def measure_distances_cycles(s1, s2, distances_dict):
        distance_values = []
        for dist_name in distances_dict:
            f = distances_dict[dist_name]
            distance_values.append(f.compute_distance_(s1, s2))
        return distance_values
        
            
    @staticmethod
    @deprecated(deprecated_in="0.8.0", removed_in="0.9.0", details="Use CyclePerturbationHelper.perturb_cycles(...) from perturbations.py instead")
    def perturb_cycles(df, cycle_col, tags_col, signal_col, perturbations_dict, tags_list = 'all'):
        df_test = df.copy()
        perturb_list = []
        cycles_list = df_test[cycle_col].unique()

        if tags_list == 'all':
            tags_list_new = df_test[tags_col].unique()
        else:
            tags_list_new = list(set(df_test[tags_col].unique()) & set(tags_list))
            
        for cycle in cycles_list:
            df_cycle = df_test[df_test[cycle_col] == cycle]
            for tag in tags_list_new:
                idxvals = df_cycle[df_cycle[tags_col] == tag].index
                tmp_arr = df_cycle.loc[idxvals, (signal_col)].values
                for pert_name in perturbations_dict:
                    pert_class = perturbations_dict[pert_name]
                    tmp_arr = pert_class.perturb_transform_(tmp_arr)            
                df_test.loc[idxvals, (signal_col)] = tmp_arr
        return df_test
    
    
    @staticmethod
    def create_tag_distance_columns(tags_list, distances_list):
        tag_distance_cols = []
        for tag in tags_list:
            for distance in distances_list:
                new_col = tag + "_" + distance
                tag_distance_cols.append(new_col)
                
        return tag_distance_cols
    
    @staticmethod
    def create_distance_matrix(df, golden_cycle_df, golden_ref_no = None, 
                               cycle_col = None, tags_col = None, signal_col = None, 
                               distances_dict = None, tags_list = None):
    
        cycles = set(df[cycle_col])
        master_table = []
        distances_list = list(distances_dict.keys())
        tag_distance_cols = DataPreparation.create_tag_distance_columns(tags_list = tags_list, distances_list = distances_list)
        for cycle in tqdm(cycles):
            if cycle == golden_ref_no:
                continue
                
            cycle_vals = []
            df_temp = df[df[cycle_col] == cycle]
            cycle_tags = df_temp[tags_col].unique()
            for tag in tags_list:
                if tag in cycle_tags:
                    ts1 = df_temp[df_temp[tags_col] == tag][signal_col].values
                    ts2 = golden_cycle_df[golden_cycle_df[tags_col] == tag][signal_col].values 
                    distances = DataPreparation.measure_distances_cycles(ts1, ts2, distances_dict=distances_dict)
                    cycle_vals.extend(distances)
                else:
                    cycle_vals.extend(repeat(np.nan, len(distances_dict.keys())))
            cycle_vals.append(cycle)
            master_table.append(cycle_vals)
	
        tag_distance_cols.append('cycle')
        master_df = pd.DataFrame(master_table, columns = tag_distance_cols)
        return master_df


# Defines the main classes
class SignalSegment:
    """
    Segment signal into sub-signals based on rules specified
    in a segmentation function (segmenting_rule_fn())
    """

    def __repr__(self):
        return """Segmentation of signal into sub-signals based on 
        rules specified in segmenting_rule_fn()
        """

    def get_segments(self, df, segmenting_rule_fn, signal_col, order_columns = True):
        """
        Apply segmentation logics.
        
        Parameters
        ----------
        df: Pandas Data Frame
            Contains data structured using the following columns: tag, time, *signal_col*

        segmenting_rule_fn: function
            Function according to which splitting is done

        signal_col : str
            The "value" column contains time signal values that can 
            be split into sub-signal (cycles)

        order_columns: boolean, optional (default is True)
            For the segmentation logics to work, data in df should be 
            ordered by "time". The method orders the data by default
            
        Returns
        ----------
        df: Pandas Data Frame
            Contains data as in the original data frame, with an added column 
            named "cycle" reporting the sub-signal number
        
        """
        
        try:
            df.drop(["svalue", "status", "flags"], axis = 1, inplace=True)
        except:
            pass
        
        df[signal_col] = pd.to_numeric(df[signal_col], errors='coerce')
        df.dropna(inplace=True)
        df.time = pd.to_datetime(df.time)
        
        if order_columns == True:
            df.sort_values(by=["time"], inplace=True)
        
        df = df.reset_index(drop=True)
        
        cycle_index = df[segmenting_rule_fn(df)].index
        logging.debug("Found {} breaking points. First three are:".format(len(cycle_index)))
        logging.debug("{}".format(df[df.index == cycle_index[0]].time))
        logging.debug("{}".format(df[df.index == cycle_index[1]].time))
        logging.debug("{}".format(df[df.index == cycle_index[2]].time))
        
        logging.debug(cycle_index)
        
        df['cycle'] = np.nan
        #df['cycle'][cycle_index] = np.arange(1,len(cycle_index)+1)
        
        logging.debug(np.arange(1,len(cycle_index)+1))
        
        df.loc[cycle_index, ('cycle')] = np.arange(1,len(cycle_index)+1)
        df = df.fillna(method='ffill')
        df = df.fillna(0)
        df['cycle'] = df.cycle.astype('int')
        return df
        

class SignalSegmentClean:
    """
    Eliminate those signals with durations that are too short or too long
    """
    
    def __init__(self, tag_name_list):
        """
        Class constructor.
        
        Parameters
        ----------
        tag_name_list: string
            list of names of tags that class focuses on
        """
        self.__tag_name_list = tag_name_list


    def __repr__(self):
        return """ Cleaning signal with tag names '{}'
        """.format(self.__tag_name_list)
    
    
    def prune_segments(self, df, low_perc = 0.25, hi_perc = 0.75):
        """
        Apply cleaning logics. Discard sub-signals (cycles) that are too short or too long
        
        Parameters
        ----------
        df: Pandas Data Frame
            contains data structured using the following columns: 
            tag, time, value, cycle
            Any df passed through preprocessing.segmentation will follow 
            this canonical form

        low_perc: float, optional (default: 0.25)
            low percentile: cycles having duration lower than low_perc 
            are discarded from the data set
            
        hi_perc: float, optional (default: 0.75)
            high percentile: cycles having duration higher than hi_perc 
            are discarded from the data set
            
        Returns
        ----------
        df: Pandas Data Frame, containing only values related to 
            tag_name_list and cleaned up from cycles that are too short or too long
            
        """
        df_clean = df[df.tag.isin(self.__tag_name_list)]

        logger.info("""Aggregating all sub-signals and pruning at cutoff points. 
        This might take some time.""")
            
        control = df_clean.groupby(['cycle']).agg({ 'time' : [min, max]}).time
        control['tot'] = (control['max'] - control['min']).dt.total_seconds()
        logger.debug(control)
        logger.info("Cutting cycles having durations out of [{}, {}]".format(np.quantile(control.tot,low_perc), np.quantile(control.tot,hi_perc)))
        control_index = control[(control.tot<=np.quantile(control.tot,hi_perc)) 
                                & (control.tot>=np.quantile(control.tot,low_perc))].index.to_list()

        df_clean = df_clean[df_clean.cycle.isin(control_index)]
        return df_clean


# Defines the user interface
def segmentation(df, segmenting_rule_fn, signal_col='value', order_columns = True):

    """
    Function that returns a DataFrame of signals segmented 
    from a longer signal using some specified rule(s)

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the signal to be segmented

    segmenting_rule_fn: function
        Function according to which the segmentation is done
    
    signal_col: str, optional (default = 'value')
        The "value" column contains time signal values that can 
        be split into sub-signal (cycles)
    
    order_columns : boolean, optional (default = True)
        For the segmentation logics to work, data in df should be 
        ordered by "time". The method orders the data by default

    Returns
    --------
    df: pandas.DataFrame
        Contains data as in the original data frame, with an added column 
        named "cycle" reporting the sub-signal number

    """

    segment_instance = SignalSegment()
    segmented_df = segment_instance.get_segments(df, segmenting_rule_fn, 
                                                signal_col, order_columns=True)

    return segmented_df


def prune(df, tag_name_list, low_perc = 0.25, hi_perc = 0.75):
    """
    Function that prunes a signal segment based on the cutoff points

    Parameters
    -----------
    df: pandas.DataFrame
        Contains data structured using the following columns: 
        tag, time, value, cycle
        Any df passed through preprocessing.segmentation will follow 
        this canonical form

    tag_name_list: str
        List of names of tags pruning focuses on
    
    low_perc: float, optional (default: 0.25)
        Low percentile: cycles having duration lower than low_perc 
        are discarded from the data set
            
        hi_perc: float, optional (default: 0.75)
        High percentile: cycles having duration higher than hi_perc 
        are discarded from the data set
            
    Returns
    ----------
    df: pandas.DataFrame
        Containing only values related to tag_name_list and 
        cleaned up from cycles that are too short or too long

    """

    prune_instance = SignalSegmentClean(tag_name_list)
    pruned_df = prune_instance.prune_segments(df, low_perc, hi_perc)

    return pruned_df


def ts_train_test_split(df_ts, **kwargs):

    """
    Function that splits a dataframe into train and test components

    Parameters:
    -----------
        df_ts: pandas.DataFrame
            The input dataframe

        kwargs: dict
        Other arguments
            train_size: float, default = 0.8
                Fraction of the input dataframe to be allocated to the train split

            test_size: float, default = 0.2
                Fraction of the input dataframe to be allocated to the test split

            shuffle: bool, default = True
                Whether or not the input dataframe is shuffled

    Returns:
    ---------
        df_train: pandas.DataFrame
            The train split

        df_test: pandas.DataFrame
            The test split

    """
    
    train_size = kwargs.pop('train_size', None)
    test_size = kwargs.pop('test_size', None)
    shuffle = kwargs.pop('shuffle', True)
    
    default_train_size = 0.8
    
    if train_size is None and test_size is None:
        train_size = default_train_size
        
    if train_size and test_size:
        raise TypeError("Only one of train_size or test_size needs to be specified, not both")
    
    if kwargs:
        raise TypeError("Invalid parameters passed")
    
    cycles = df_ts.cycle.unique()
    n_cycles = len(cycles)
    
    if shuffle:
        random.shuffle(cycles)
        
    cutpoint = round(train_size * n_cycles)  
    
    df_train = df_ts[df_ts.cycle.isin(cycles[:cutpoint])]
    df_test = df_ts[df_ts.cycle.isin(cycles[cutpoint:])]
    
    return df_train, df_test