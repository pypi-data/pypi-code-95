#!/usr/bin/env python
# coding: utf-8

# %%
import os
import re

from numpy import random
import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path

from datetime import datetime

from .utils import (keydefaultdict, plot_pandas_categorical_features, mkdir_ifnotexist, load_pickle, save_pickle)
from .mlutils import bucketize_into_bins, get_discrete_labels
from .utils import BaseAttrDict

from scipy.io.arff import loadarff

pd.options.display.max_columns = 50

# %%
PACKAGE_DATA_FOLDER = os.path.abspath(os.path.join(Path(__file__).parent, 'data'))

# KAGGLE Message
KAGGLE_LINK = {
    'lendingclub': 'wordsforthewise/lending-club',
}


def kaggle_dataset(folder):
    mkdir_ifnotexist(folder)

    if len(os.listdir(folder)) > 0:
        return True

    else:
        # Get the dataset short name (folder name)
        dataset = os.path.basename(os.path.dirname(os.path.join(folder, '.placeholder')))
        if dataset in KAGGLE_LINK:
            dataset_link = KAGGLE_LINK[dataset]
        else:
            raise ValueError(f'No link for this Kaggle dataset ({dataset}).')

        # Print the message to download
        print(
            f"""
This dataset is not directly available in this library. It will be downloaded using kaggle.
Please make sure that ~/.kaggle/kaggle.json is available and correctly configured.

To make the dataset available through this library please download it using:
    kaggle datasets download --unzip -d {dataset_link} -p {folder}


- To install kaggle use `pip install kaggle`
- If you are behind a proxy you must set it using: `kaggle config set -n proxy -v http://yourproxy.com:port`
- If you wish to download the dataset to another location other than the library location please pass an appropriate `folder` argument.
        """
        )

        return False


# %%


def load_lendingclub(
    folder=os.path.join(PACKAGE_DATA_FOLDER, 'lendingclub'),
    load_preprocessed=True,
    cleaning_type='ax',
    random_state=2020,
):
    random_state = np.random.RandomState(random_state)

    def target_clean(df):
        # Non-completed loans
        df = df[df['loan_status'] != 'Current']
        df = df[df['loan_status'] != 'In Grace Period']

        # The taget must not be NaN
        df = df.dropna(how='any', subset=['loan_status'])

        # Recode targets
        df['loan_status'] = df.loan_status.map(
            {
                'Fully Paid': 0,
                'Charged Off': 1,
                'Late (31-120 days)': 1,
                'Late (16-30 days)': 1,
                'Does not meet the credit policy. Status:Fully Paid': 0,
                'Does not meet the credit policy. Status:Charged Off': 1,
                'Default': 1
            }
        )
        return df.reset_index(drop=True).copy()

    def basic_cleaning(df):
        # Drop columns with NaN more than 90%
        drop_cols = df.columns[df.isnull().mean() > 0.9]
        df = df.drop(drop_cols, axis=1)

        # Drop records with more than 50% of NaN features
        df = df[(df.isnull().mean(axis=1) < .5)]

        df['verification_status'] = df.verification_status.map({'Verified': 0, 'Source Verified': 1, 'Not Verified': 2})
        df['debt_settlement_flag'] = df.debt_settlement_flag.map({'N': 0, 'Y': 1})
        df['initial_list_status'] = df.initial_list_status.map({'w': 0, 'f': 1})
        df['application_type'] = df.application_type.map({'Individual': 0, 'Joint App': 1})
        df['hardship_flag'] = df.hardship_flag.map({'N': 0, 'Y': 1})
        df['pymnt_plan'] = df.pymnt_plan.map({'n': 0, 'y': 1})
        df['disbursement_method'] = df.disbursement_method.map({'Cash': 0, 'DirectPay': 1})
        df['term'] = df.term.map({' 36 months': 0, ' 60 months': 1})
        df['grade'] = df['grade'].map({v: i for i, v in enumerate(np.sort(df['grade'].unique()))})
        df['sub_grade'] = df['sub_grade'].map({v: i for i, v in enumerate(np.sort(df['sub_grade'].unique()))})
        df['emp_length'] = df['emp_length'].apply(
            lambda x: x.replace('year', '').replace('s', '').replace('+', '').replace('< 1', '0')
            if isinstance(x, str) else '-1'
        ).astype(int)
        df['earliest_cr_line'] = df['earliest_cr_line'].apply(lambda x: int(x[-4:]))
        df['issue_d'] = pd.to_datetime(df['issue_d'])

        # Get rid of few customers with no home
        df = df[df['home_ownership'].apply(lambda x: x in ['OWN', 'RENT', 'MORTGAGE'])]
        df['home_ownership'] = df.home_ownership.map({'MORTGAGE': 0, 'OWN': 1, 'RENT': 2})

        return df.reset_index(drop=True).copy()

    def ax_cleaning(df):
        COLUMNS = ['loan_status', 'issue_d'] + sorted(
            [
                'loan_amnt', 'term', 'int_rate', 'installment', 'grade', 'sub_grade', 'emp_length', 'home_ownership',
                'annual_inc', 'verification_status', 'dti', 'earliest_cr_line', 'open_acc', 'pub_rec', 'revol_bal',
                'revol_util', 'total_acc', 'application_type', 'mort_acc', 'pub_rec_bankruptcies'
            ]
        )

        feature = 'dti'
        filtercol = (df[feature] < 0)
        df[feature][filtercol] = random_state.normal(24.5, .5, size=int((filtercol).sum()))
        filtercol = (df[feature].isnull())
        df[feature][filtercol] = -1

        feature = 'pub_rec_bankruptcies'
        filtercol = (df[feature].isnull())
        df[feature][filtercol] = df[feature].median()

        feature = 'mort_acc'
        filtercol = (df[feature].isnull())
        df[feature][filtercol] = 52

        feature = 'revol_util'
        filtercol = (df[feature].isnull())
        df[feature][filtercol] = random_state.normal(82.5, 3, size=int((filtercol).sum()))

        return df[COLUMNS].reset_index(drop=True).copy()

    if kaggle_dataset(folder) is False:
        return None

    PREPROCESSED_FILENAME = os.path.join(folder, f'preprocessed_{cleaning_type}.pkl')

    if load_preprocessed and os.path.exists(PREPROCESSED_FILENAME):
        return load_pickle(PREPROCESSED_FILENAME)
    else:
        df = pd.read_csv(os.path.join(folder, 'accepted_2007_to_2018q4.csv/accepted_2007_to_2018Q4.csv'))
        df = target_clean(df)
        df = basic_cleaning(df)

        if cleaning_type == 'ax':
            df = ax_cleaning(df)
        else:
            raise ValueError('Invalid cleaning type specified.')

    dataset = BaseAttrDict(
        data=df.reset_index(drop=True), class_names=['Good', 'Bad'], target_name='loan_status', split_date='issue_d'
    )

    save_pickle(dataset, PREPROCESSED_FILENAME)

    return dataset


# %%
# def load_toy_financial():
#     """
#         ____ _ _  _ ____ _  _ ____ ____    ___ ____ _   _
#         |___ | |\ | |__| |\ | |    |___     |  |  |  \_/
#         |    | | \| |  | | \| |___ |___     |  |__|   |

#     """

#     FEATURES = W, D, H, N = ['Warning', 'Devaluation', 'House Crash', 'Negative News']
#     CLASSES = C, E = ['Drop Consumer Confidence', 'External Problem']
#     data = pd.DataFrame(
#         [
#             [0, 0, 0, 0, 0, 0],
#             [0, 0, 1, 0, 1, 1],
#             [0, 1, 0, 0, 1, 1],
#             [0, 1, 1, 0, 1, 1],
#             [1, 0, 0, 0, 0, 0],
#             [1, 0, 1, 0, 0, 0],
#             [1, 1, 0, 0, 1, 1],
#             [1, 1, 1, 0, 1, 1],
#             [0, 0, 0, 1, 1, 0],
#             [0, 0, 1, 1, 1, 0],
#             [0, 1, 0, 1, 1, 0],
#             [0, 1, 1, 1, 1, 0],
#             [1, 0, 0, 1, 1, 1],
#             [1, 0, 1, 1, 1, 1],
#             [1, 1, 0, 1, 1, 1],
#             [1, 1, 1, 1, 1, 1],
#         ],
#         columns=FEATURES + CLASSES
#     )
#     for col in data:
#         data[col] = data[col].apply(lambda x: '+' if x == 1 else '-')

#     # Create Bayesian Network
#     net = nx.DiGraph()
#     for node in FEATURES + CLASSES:
#         net.add_node(node)
#     for a, b in [(E, C), (E, W), (C, D), (C, H), (C, N), (D, H)]:
#         net.add_edge(a, b)

#     return data, CLASSES, net


# %%
def load_adult(folder=os.path.join(PACKAGE_DATA_FOLDER, 'adult')):
    """
    ____ ___  _  _ _    ___ 
    |__| |  \ |  | |     |  
    |  | |__/ |__| |___  |  
                        
    """
    with open(os.path.join(folder, "adult.names")) as f:
        names = [line.split(':')[0] for line in f.readlines()[-15:] if ":" in line]
    df = pd.read_csv(os.path.join(folder, "adult.data"), header=None, names=names + ['class'], index_col=False)
    return df


# %%


def load_heloc(folder=os.path.join(PACKAGE_DATA_FOLDER, 'heloc'), random_state=2020, cleaning_type='default_clean'):
    """"
    _  _ ____ _    ____ ____ 
    |__| |___ |    |  | |    
    |  | |___ |___ |__| |___ 

    Description of the dataset can be found here: http://dukedatasciencefico.cs.duke.edu/models/
                         
    """
    random_state = np.random.RandomState(random_state)

    def clean_heloc(data):
        data['RiskPerformance'] = data['RiskPerformance'].apply(lambda x: 1 if 'Bad' in x else 0)
        all_special_mask = np.all(
            ((data.drop(columns=['RiskPerformance']) <= -7) & (data.drop(columns=['RiskPerformance']) >= -9)).values,
            axis=1
        )
        data = data[~all_special_mask]
        data = data[np.sort(data.columns.values)]
        data['ExternalRiskEstimate'][data['ExternalRiskEstimate'] < 0] = data['ExternalRiskEstimate'].median()
        data['MSinceMostRecentDelq'][data['MSinceMostRecentDelq'] < 0] = \
            random_state.uniform(30, 80, int((data['MSinceMostRecentDelq'] < 0).sum())).astype(int)

        data['MSinceMostRecentInqexcl7days'][data['MSinceMostRecentInqexcl7days'] == -7] = -1
        data['MSinceMostRecentInqexcl7days'][data['MSinceMostRecentInqexcl7days'] == -8] = 25
        data['MSinceOldestTradeOpen'][data['MSinceOldestTradeOpen'] == -8] = random_state.uniform(
            145, 165, int((data['MSinceOldestTradeOpen'] == -8).sum())
        ).astype(int)
        data['NetFractionInstallBurden'][data['NetFractionInstallBurden'] == -8] = random_state.normal(
            data['NetFractionInstallBurden'].median(), 7.5, size=int((data['NetFractionInstallBurden'] == -8).sum())
        ).astype(int)
        data['NetFractionRevolvingBurden'][data['NetFractionRevolvingBurden'] == -8] = random_state.normal(
            75, 5, size=int((data['NetFractionRevolvingBurden'] == -8).sum())
        ).astype(int)
        data['NumInstallTradesWBalance'][data['NumInstallTradesWBalance'] == -8] = 0
        data['NumRevolvingTradesWBalance'][data['NumRevolvingTradesWBalance'] == -8] = random_state.normal(
            13, 1, size=int((data['NumRevolvingTradesWBalance'] == -8).sum())
        ).astype(int)
        data['NumBank2NatlTradesWHighUtilization'][data['NumBank2NatlTradesWHighUtilization'] == -8] = 20
        data['PercentTradesWBalance'][data['PercentTradesWBalance'] == -8] = data['PercentTradesWBalance'].median()

        return data.reset_index(drop=True).copy()

    df = pd.read_csv(os.path.join(folder, 'HELOC.csv'))
    if 'default_clean' in cleaning_type:
        df = clean_heloc(df)

    return BaseAttrDict(
        data=df,
        target_name='RiskPerformance',
        class_names=['Good', 'Bad'],
    )


# %%


def load_fico(
    main_data_path, folder='fico', order='natural', original=False, BINS_STRATEGY=None, N_BINS=None, NB_BINS=None
):
    """
    ____ _ ____ ____ 
    |___ | |    |  | 
    |    | |___ |__| 
                    
    """

    if original:
        df = pd.read_csv(os.path.join(main_data_path, folder, 'heloc_dataset_v1.csv'))
        label = 'RiskPerformance'

        df_string = df.copy()

        for c, col in enumerate(df_string.columns.values):
            if df_string.dtypes[col] != 'object' and col != label:  # Do not bucketize categorical feature
                df_string[col], col_labels = bucketize_into_bins(
                    df_string[col], N_BINS, retlabels=True, strategy=BINS_STRATEGY
                )
                df_string[col] = df_string[col].apply(lambda x: col_labels[x])
        df_string[label] = pd.get_dummies(df_string[label])[['Bad']]

        decoder = None

    else:
        df = pd.read_csv(os.path.join(main_data_path, folder, 'WOE_Rud_data.csv'))
        keys = pd.read_csv(os.path.join(main_data_path, folder, 'keys.csv'))

        y = pd.read_csv(os.path.join(main_data_path, folder, 'y_data.csv'))
        label = 'RiskPerformance'
        df.insert(loc=0, column=label, value=pd.get_dummies(y[label])[['Bad']])

        df_string = df.copy()

        if order == 'natural':
            decoder = {}
            decoder[label] = {i: val for i, val in enumerate(['0', '1'])}
            for col in keys['feature'].unique():
                #     key = keys['sort_val'][keys['feature']==col]
                vals = round(keys['value'][keys['feature'] == col], 3).unique().astype(str)
                decoder[col] = {i: val for i, val in enumerate(list(vals))}

            df_string = round(df_string, 3).astype(str)
        else:
            df_string = df_string - df_string.min()
            df_string = df_string.astype(str)
            decoder = None

    return df_string, label, decoder


def load_water(main_data_path, folder='water_quality', complexity='hard'):
    """
        _ _ _ ____ ___ ____ ____    ____ _  _ ____ _    _ ___ _   _ 
        | | | |__|  |  |___ |__/    |  | |  | |__| |    |  |   \_/  
        |_|_| |  |  |  |___ |  \    |_\| |__| |  | |___ |  |    |   
                                                                    
    """

    raw_data = loadarff(os.path.join(main_data_path, folder, 'water-quality-nom.arff'))
    df = pd.DataFrame(raw_data[0])
    for f in df.columns.values:
        df[f] = df[f].astype(int)

    labels = df.columns.values[-14:]

    for col in labels:
        df[col] = df[col].apply(lambda x: get_discrete_labels(2, 'binary')[x])

    def bucketize_and_apply_labels(col, *args, **kargs):
        df[col], col_values, col_labels = bucketize_into_bins(
            df[col].values, *args, retlabels=True, retbins=True, strategy='uniform', label_type='generic', **kargs
        )
        df[col] = df[col].apply(lambda x: col_labels[x])
        print(col, col_values)

    if complexity == 'hard':
        for col in ['std_temp', 'std_pH', 'o2', 'o2sat', 'sio2']:
            bucketize_and_apply_labels(col, 3)

        for col in ['conduct', 'hardness']:
            df[col] = (df[col] >= 2) * 1 + (df[col] >= 3) * 1 + (df[col] >= 4) * 1 + (df[col] >= 5) * 1
            bucketize_and_apply_labels(col, 5)

        for col in ['no3']:
            df[col] = (df[col] >= 1) * 1 + (df[col] >= 2) * 1 + (df[col] >= 3) * 1
            bucketize_and_apply_labels(col, 4)

        for col in ['co2', 'no2', 'nh4', 'po4', 'cl', 'kmno4', 'k2cr2o7', 'bod']:
            df[col] = (df[col] >= 1) * 1
            bucketize_and_apply_labels(col, 2)

    elif complexity == 'medium':
        for col in ['std_temp', 'std_pH', 'o2', 'o2sat']:
            bucketize_and_apply_labels(col, 3)

        for col in ['conduct']:
            df[col] = (df[col] >= 2) * 1 + (df[col] >= 4) * 1
            bucketize_and_apply_labels(col, 3)

        for col in ['hardness']:
            df[col] = (df[col] >= 3) * 1 + (df[col] >= 5) * 1
            bucketize_and_apply_labels(col, 3)

        for col in ['no3', 'sio2']:
            df[col] = (df[col] >= 2) * 1
            bucketize_and_apply_labels(col, 2)

        for col in ['co2', 'no2', 'nh4', 'po4', 'cl', 'kmno4', 'k2cr2o7', 'bod']:
            df[col] = (df[col] >= 1) * 1
            bucketize_and_apply_labels(col, 2)

    elif complexity == 'easy':
        for col in ['std_temp', 'std_pH', 'o2', 'o2sat']:
            bucketize_and_apply_labels(col, 2)

        for col in ['conduct']:
            df[col] = (df[col] >= 4) * 1  # + (df[col] >= 4) * 1
            bucketize_and_apply_labels(col, 2)

        for col in ['hardness']:
            df[col] = (df[col] >= 5) * 1  # + (df[col] >= 5) * 1
            bucketize_and_apply_labels(col, 2)

        for col in ['no3', 'sio2']:
            df[col] = (df[col] >= 2) * 1
            bucketize_and_apply_labels(col, 2)

        for col in ['co2', 'no2', 'nh4', 'po4', 'cl', 'kmno4', 'k2cr2o7', 'bod']:
            df[col] = (df[col] >= 1) * 1
            bucketize_and_apply_labels(col, 2)

    return df, labels


# %%


def load_california(main_data_path, BINS, BINS_STRATEGY, NB_BINS, folder="california"):
    """
        ____ ____ _    _ ____ ____ ____ _  _ _ ____ 
        |    |__| |    | |___ |  | |__/ |\ | | |__| 
        |___ |  | |___ | |    |__| |  \ | \| | |  | 
                                            
    """
    df = pd.read_csv(os.path.join(main_data_path, folder, 'housing_with_feature_engineering.csv'))
    LABEL = 'median_house_value'

    for c, col in enumerate(df.columns.values):
        if df.dtypes[col] != 'object' and col != LABEL:  # Do not bucketize categorical feature
            df[col], col_labels = bucketize_into_bins(
                df[col],
                BINS[c],  # args.NB_BINS, 
                retlabels=True,
                strategy=BINS_STRATEGY,
                label_type='generic'
            )
            df[col] = df[col].apply(lambda x: col_labels[x])
    df[LABEL], col_labels = bucketize_into_bins(df[LABEL], NB_BINS, retlabels=True, label_type='generic')
    df[LABEL] = df[LABEL].apply(lambda x: col_labels[x])
    LABELS = [LABEL]

    return df, LABELS


# %%
def load_earthquake_police(categorical=True):
    """
    ____ ____ ____ ___ _  _ ____ _  _ ____ _  _ ____ 
    |___ |__| |__/  |  |__| |  | |  | |__| |_/  |___ 
    |___ |  | |  \  |  |  | |_\| |__| |  | | \_ |___ 
                                                 
        Earthquake : 12 samples, 3 features, 2 classifications
    """
    FEATURES = V, M, P = ['Feel Vibration', 'Mary Calls', 'Police Calls']
    CLASSES = A, E = ['Alarm', 'Earthquake']
    # Create dataset
    data = pd.DataFrame(
        [
            #V, M, P->A, E
            [0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 1, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1],
            [2, 0, 0, 0, 2],
            [2, 0, 1, 1, 2],
            [2, 1, 0, 1, 2],
            [2, 1, 1, 1, 2],
        ],
        columns=FEATURES + CLASSES
    )
    # Create Bayesina Network
    net = nx.DiGraph()
    for node in FEATURES + CLASSES:
        net.add_node(node)
    for a, b in [(A, M), (A, P), (E, V), (E, A)]:
        net.add_edge(a, b)

    if categorical:
        for col in [V, E]:
            data[col] = data[col].apply(lambda x: 'Weak' if x == 1 else 'Strong' if x == 2 else 'No')
        for col in [M, P, A]:
            data[col] = data[col].apply(lambda x: 'Yes' if x == 1 else 'No')

    return data, FEATURES, CLASSES, net


def load_amphibians(main_data_path, folder='amphibians'):
    """
        ____ _  _ ___  _  _ _ ___  _ ____ _  _ ____ 
        |__| |\/| |__] |__| | |__] | |__| |\ | [__  
        |  | |  | |    |  | | |__] | |  | | \| ___] 
                                                    
        Note: This are actually 2 datasets (depending on subject):
            - por(tuguese) (~600)
            - mat(h) (~300)
                -> Most of the students in math are also in portuguese
    """
    df = pd.read_csv(os.path.join(main_data_path, folder, 'dataset.csv'), sep=';', skiprows=1, index_col='ID')
    labels = df.columns.values[-7:]

    #     display(df)

    for col in ['SR']:
        df[col], col_labels = bucketize_into_bins(
            df[col].values, strategy='quantile', nb_bins=3, retlabels=True, label_type='generic'
        )
        df[col] = df[col].apply(lambda x: col_labels[x])

    for col in ['NR']:
        df[col], col_labels = bucketize_into_bins(
            df[col].values, strategy='uniform', nb_bins=3, retlabels=True, label_type='generic'
        )
        df[col] = df[col].apply(lambda x: col_labels[x])

    for col in labels:
        df[col] = df[col].apply(lambda x: get_discrete_labels(2, 'binary')[x])

    df = df.apply(lambda col: col.apply(lambda x: str(x)))
    return df, labels


def load_student(
    main_data_path,
    subject='portuguese',
    one_hot_ordinal=True,
    nb_bins_scores=3,
    nb_bins_numeric=4,
    nb_bins_classes=5,
    folder='student'
):
    """
        ____ ___ _  _ ___  ____ _  _ ___ 
        [__   |  |  | |  \ |___ |\ |  |  
        ___]  |  |__| |__/ |___ | \|  |  
                                        

        Note: This are actually 2 datasets (depending on subject):
            - por(tuguese) (~600)
            - mat(h) (~300)
                -> Most of the students in math are also in portuguese
    """
    df = pd.read_csv(
        os.path.join(main_data_path, folder, f'student-{subject[:3]}.csv'),
        sep=';',
    )

    education = {0: 'none', 1: 'primary <=4th', 2: 'primary >4th', 3: 'secondary', 4: 'higher'}
    travel_time = {1: '<15 min', 2: '15-30 min', 3: '30-60 min', 4: '>1 hour'}
    study_time = {1: '<2 h', 2: '2-5 h', 3: '5-10 h', 4: '>10 h'}
    for col in ['Fedu', 'Medu']:
        if one_hot_ordinal:
            for v, name in list(education.items())[1:]:
                df[col + '>=' + name] = df[col].apply(lambda x: 'yes' if x >= v else 'no')
            del df[col]
        else:
            df[col] = df[col].apply(lambda x: education[x])
    for col in ['Mjob', 'Fjob']:
        df[col] = df[col].apply(lambda x: x.replace('_', ' '))
    df['age'] = df['age'].apply(lambda x: (str(x) if x < 20 else '>=20') + ' yro')
    df['Pstatus'] = df['Pstatus'].apply(lambda x: {'T': 'together', 'A': 'apart'}[x])
    df['address'] = df['address'].apply(lambda x: {'R': 'rural', 'U': 'urban'}[x])
    df['famsize'] = df['famsize'].apply(lambda x: {'GT3': '>=4', 'LE3': '<4'}[x])
    df['traveltime'] = df['traveltime'].apply(lambda x: travel_time[x])
    df['studytime'] = df['studytime'].apply(lambda x: study_time[x])

    scores = ['famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health']
    numeric = ['absences']
    classes = ['G1', 'G2', 'G3']

    # Score-like features
    nb_bins_scores = min(5, nb_bins_scores)
    for col in scores:
        df[col], col_labels = bucketize_into_bins(
            df[col].values, strategy='uniform', nb_bins=nb_bins_scores, retlabels=True, label_type='generic'
        )
        df[col] = df[col].apply(lambda x: col_labels[x])

    # Numeric
    for col in numeric:
        df[col], col_labels = bucketize_into_bins(
            df[col].values, strategy='quantile', nb_bins=nb_bins_numeric, retlabels=True, label_type='generic'
        )
        df[col] = df[col].apply(lambda x: col_labels[x])

    # Classes
    for col in classes:
        df[col], col_labels = bucketize_into_bins(
            df[col].values, strategy='quantile', nb_bins=nb_bins_classes, retlabels=True, label_type='generic'
        )
        df[col] = df[col].apply(lambda x: col_labels[x])

    return df, classes


# %%
def load_university_admission():
    """"
        _  _ _  _ _ _  _ ____ ____ ____ _ ___ _   _    ____ ___  _  _ _ ____ ____ _ ____ _  _ 
        |  | |\ | | |  | |___ |__/ [__  |  |   \_/     |__| |  \ |\/| | [__  [__  | |  | |\ | 
        |__| | \| |  \/  |___ |  \ ___] |  |    |      |  | |__/ |  | | ___] ___] | |__| | \|                                                                               
    """

    return pd.DataFrame(
        [
            [0, 0, 0, 0, 0], [0, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 0, 1, 1, 0], [0, 1, 0, 0, 0], [0, 1, 0, 1, 0],
            [0, 1, 1, 0, 0], [0, 1, 1, 1, 1], [1, 0, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 0, 0], [1, 0, 1, 1, 1],
            [1, 1, 0, 0, 0], [1, 1, 0, 1, 1], [1, 1, 1, 0, 1], [1, 1, 1, 1, 1]
        ],
        columns=['W', 'F', 'E', 'G', 'class']
    )


# %%
def load_votes_dataset(main_data_path, folder='house-votes', mock_features_names=False, shorten_names=True):
    """
        _  _ ____ ___ ____ ____ 
        |  | |  |  |  |___ [__  
         \/  |__|  |  |___ ___] 
                        
        (UCI ML Repo)    
    """

    # Encoder
    VOTES_ENCODER = {'y': 'yes', 'n': 'no'}

    # Parsing features/class names and values
    with open(os.path.join(main_data_path, folder, 'house-votes-84.names'), 'r') as file:
        texts = [
            s.split('.')[1].strip() for s in file.read().split('Attribute Information:')
            [1].split('8. Missing Attribute Values:')[0].strip().split('\n')
        ]
        features_values = [s.split('(')[1].split(')')[0].split(',') for s in texts]
        features_values = [[s.strip() for s in sub] for sub in features_values]
        # class_values = features_values[0]
        features_values = features_values[1:]
        features_names = [s.split(':')[0].strip() for s in texts][1:]

    # Load into a pandas DataFrame
    data = pd.read_csv(
        os.path.join(main_data_path, folder, 'house-votes-84.data'), names=['party'] + features_names, header=None
    )
    if mock_features_names:
        data.columns = ['class'] + [f'F{i}' for i in range(len(data.columns) - 1)]
    data = data.apply(lambda s: s.apply(lambda x: VOTES_ENCODER[x] if x in VOTES_ENCODER else x))

    if shorten_names:
        data.rename(
            columns={
                #          "handicapped-infants": "handic",
                #         "water-project-cost-sharing": "water",
                #         "adoption-of-the-budget-resolution": "budget",
                #         "physician-fee-freeze": "physic",
                #         "el-salvador-aid": "elsal",
                #         "religious-groups-in-schools": "relig",
                #         "anti-satellite-test-ban": "satel",
                #         "aid-to-nicaraguan-contras": "nicar",
                #         "mx-missile": "missil",
                #         "immigration": "immig",
                #         "synfuels-corporation-cutback": "synfue",
                #         "education-spending": "edu",
                #         "superfund-right-to-sue": "sue",
                #         "crime": "crime",
                #         "duty-free-exports": "expor",
                #         "export-administration-act-south-africa": "safr",
                "handicapped-infants": "handicapped\ninfants",
                "water-project-cost-sharing": "water\nproject",
                "adoption-of-the-budget-resolution": "budget\nresolution",
                "physician-fee-freeze": "physician\nfee freeze",
                "el-salvador-aid": "el salvador\naid",
                "religious-groups-in-schools": "religion\nin school",
                "anti-satellite-test-ban": "anti-satellite\ntest ban",
                "aid-to-nicaraguan-contras": "nicaraguan\naid",
                "mx-missile": "mx\nmissile",
                "immigration": "immigration",
                "synfuels-corporation-cutback": "synfuels\ncutback",
                "education-spending": "education\nspending",
                "superfund-right-to-sue": "superfund\nsuing",
                "crime": "crime",
                "duty-free-exports": "duty free\nexports",
                "export-administration-act-south-africa": "south africa\nexport",
            },
            inplace=True
        )

    return data, 'party'


# %%
def load_parole_dataset(main_data_path, folder='parole', CATEGORICAL=False, bins=[4, 4, 5]):
    """
        ___  ____ ____ ____ _    ____ 
        |__] |__| |__/ |  | |    |___ 
        |    |  | |  \ |__| |___ |___ 
                                    

        Load the Parole dataset
        CATEGORICAL : bool 
            True to preprocess the numerical features
        bins : list/tuple 
            Size of the bins of the numerical features, in order:
                - time.served
                - max.sentence
                - age

        Source: National Corrections Reporting Program, 2004 (ICPSR 26521) https://www.icpsr.umich.edu/icpsrweb/NACJD/studies/26521
        
        Note:
            - Naive Bayes Classifier Binarized doesn't work well, we need state and crime to be categorical
    """

    # Decoder
    parole_features_decoder_dict = {
        'male': {
            0: 'Female',
            1: 'Male'
        },
        'race': {
            0: 'White',
            1: 'Non-white'
        },
        'age': None,
        'state': {
            0: 'Other state',
            1: 'Kentucky',
            2: 'Louisiana',
            3: 'Virginia',
        },
        'time.served': None,
        'max.sentence': None,
        'multiple.offenses': {
            0: 'single-offender',
            1: 'multi-offender'
        },
        'crime': {
            0: 'other-crime',
            1: 'larceny',
            2: 'drug',
            3: 'driving',
        },
        'violator': {
            0: 'No',
            1: 'Yes'
        }
    }

    # Load
    df = pd.read_csv(os.path.join(main_data_path, folder, 'parole.csv'))

    # Convert to categorical
    if CATEGORICAL:
        # Create categories for continuous data
        df['race'] = df['race'] - 1
        df['state'] = df['state'] - 1
        df['crime'] = df['crime'] - 1
        df["time.served"], time_bins = pd.cut(df["time.served"], bins=bins[0], labels=False, retbins=True)
        df["max.sentence"], sentence_bins = pd.cut(df["max.sentence"], bins=bins[1], labels=False, retbins=True)
        df["age"], age_bins = pd.cut(df["age"], bins=bins[2], labels=False, retbins=True)
        parole_features_decoder_dict['age'] = {
            i: f'{int(round(abs(age_bins[i]), 0))}-{int(round(age_bins[i+1], 0))} yr.'
            for i in range(0,
                           len(age_bins) - 1)
        }
        parole_features_decoder_dict['max.sentence'] = {
            i: f'{int(round(abs(sentence_bins[i]), 0))}-{int(round(sentence_bins[i+1], 0))} yr.'
            for i in range(0,
                           len(sentence_bins) - 1)
        }
        parole_features_decoder_dict['time.served'] = {
            i: f'{int(round(abs(time_bins[i]), 0))}-{int(round(time_bins[i+1], 0))} yr.'
            for i in range(0,
                           len(time_bins) - 1)
        }

        for col in df.columns.values:
            df[col] = df[col].apply(lambda val: parole_features_decoder_dict[col][val])

        df = df.rename(
            columns={
                'time.served': 'time\nserved',
                'max.sentence': 'max\nsentence',
                'violator': 'parole\nviolator',
                'multiple.offenses': 'multiple\noffenses',
                'male': 'sex'
            }
        )

    return df, 'parole\nviolator'


# %%
""""
___  _    ____ _   _ 
|__] |    |__|  \_/  
|    |___ |  |   |   
                     
"""


def load_play_bcc():
    """
        Play : 8 samples, 3 features, 2 classifications
    """
    FEATURES = ['Temperature', 'Humidity', 'Pressure']
    CLASSES = ['Rainy', 'Play']
    data = pd.DataFrame(
        [
            #T,H,P  R,P
            [0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 0, 0],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 0, 1, 0],
            [1, 1, 1, 0, 1],
        ],
        columns=FEATURES + CLASSES
    )
    return data, data[FEATURES], data[CLASSES]


def load_play_bbcc(only_play=False, categorical=True):
    """
        Play : 16 samples, 4 features, 2 classifications
    """
    FEATURES = ['Temperature', 'Humidity', 'Pressure', 'Windy']
    CLASSES = ['Rainy', 'Play']
    data = pd.DataFrame(
        [
            #T,H,P,W  R,P
            [0, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 1],
            [0, 1, 0, 0, 1, 0],
            [0, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 1],
            [1, 1, 0, 0, 1, 0],
            [1, 1, 1, 0, 0, 1],
            [0, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 1, 1, 1, 0, 0],
            [1, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 0, 1],
            [1, 1, 0, 1, 1, 0],
            [1, 1, 1, 1, 0, 1],
        ],
        columns=FEATURES + CLASSES
    )
    if only_play:
        CLASSES = CLASSES[1:]
    if categorical:
        for col in ['Temperature', 'Humidity', 'Pressure']:
            data[col] = data[col].apply(lambda x: 'High' if x == 1 else 'Low')
        for col in ['Windy', 'Rainy', 'Play']:
            data[col] = data[col].apply(lambda x: 'Yes' if x == 1 else 'No')
    return data, FEATURES, CLASSES


def load_play_bbcc2(only_play=False, categorical=True):
    """
        Play : 18 samples, 3 features, 2 classifications
    """
    FEATURES = T, P, W = ['Temperature', 'Pressure', 'Windy']
    CLASSES = R, Outcome = ['Rainy', 'Play']
    data = pd.DataFrame(
        [
            #T,P,W  R,P
            [0, 0, 0, 1, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 2, 1, 0],
            [0, 1, 0, 0, 1],
            [0, 1, 1, 0, 0],
            [0, 1, 2, 0, 0],
            [1, 0, 0, 1, 0],
            [1, 0, 1, 1, 0],
            [1, 0, 2, 1, 0],
            [1, 1, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [1, 1, 2, 0, 1],
            [2, 0, 0, 1, 0],
            [2, 0, 1, 1, 0],
            [2, 0, 2, 1, 0],
            [2, 1, 0, 1, 0],
            [2, 1, 1, 1, 0],
            [2, 1, 2, 1, 0],
        ],
        columns=FEATURES + CLASSES
    )
    # Create Bayesina Network
    net = nx.DiGraph()
    for node in FEATURES + CLASSES:
        net.add_node(node)
    for a, b in [(Outcome, W), (Outcome, T), (Outcome, R), (R, T), (R, P)]:
        net.add_edge(a, b)

    if only_play:
        CLASSES = CLASSES[1:]
    if categorical:
        for col in [T, W]:
            data[col] = data[col].apply(lambda x: 'Medium' if x == 1 else 'High' if x == 2 else 'Low')
        for col in [P]:
            data[col] = data[col].apply(lambda x: 'High' if x == 1 else 'Low')
        for col in [R, Outcome]:
            data[col] = data[col].apply(lambda x: 'Yes' if x == 1 else 'No')
    return data, FEATURES, CLASSES, net


def load_play_nn(only_play=False):
    """
        Play : 6 samples, 2 features, 1 classification
    """
    FEATURES = ['t', 'w']
    CLASSES = ['o']
    data = pd.DataFrame(
        [
            #T,W  P
            [0, 0, 0],
            [1, 0, 1],
            [2, 0, 1],
            [0, 1, 0],
            [1, 1, 0],
            [2, 1, 1],
        ],
        columns=FEATURES + CLASSES
    )
    if only_play:
        CLASSES = CLASSES[1:]
    return data, data[FEATURES], data[CLASSES]


def load_play_naive(only_play=False):
    """
        Play : 16 samples, 4 features, 1 classification
    """
    FEATURES = ['Temperature', 'Humidity', 'Windy', 'Rainy']
    CLASSES = ['Play Golf']
    data = pd.DataFrame(
        [
            #T,H,W,R
            [0, 0, 0, 0, 1],
            [0, 0, 1, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 1, 1, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 1, 0, 1],
            [1, 1, 0, 0, 0],
            [1, 1, 1, 0, 1],
            [0, 0, 0, 1, 1],
            [0, 0, 1, 1, 1],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1],
            [1, 0, 0, 1, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 1, 0],
            [1, 1, 1, 1, 1],
        ],
        columns=FEATURES + CLASSES
    )
    if only_play:
        CLASSES = CLASSES[1:]
    return data, data[FEATURES], data[CLASSES]


# %%
def load_emotions(main_data_path, folder='emotions', nb_bins=False, strategy='quantile'):
    """"
        ____ _  _ ____ ___ _ ____ _  _ ____ 
        |___ |\/| |  |  |  | |  | |\ | [__  
        |___ |  | |__|  |  | |__| | \| ___] 

        From UCO ML Repo: http://www.uco.es/kdis/mllresources/

        72 features (numeric) and 6 labels

        nb_bins: int
            Number of bins for all the features 

        strategy: str
            bins strategy, see emals.mlutils.bucketize_into_bins
    """
    assert nb_bins is False or (isinstance(nb_bins, int) and nb_bins >= 2)

    raw_data = loadarff(os.path.join(main_data_path, folder, 'emotions.arff'))
    data = pd.DataFrame(raw_data[0])
    for col in data.columns:
        if data[col].dtype == np.object:
            data[col] = data[col].astype(float)

    def __clean_replace(col):
        col = col.replace('1298_', '')
        col = col.replace('40_', '')
        col = col.replace('Mean_', 'μ')
        col = col.replace('Std_', 'σ')
        col = col.replace('Acc', '')
        col = col.replace('Mem', '')
        col = col.replace('_', '')
        col = col.replace('Peak', '')
        col = col.replace('High', '↑')
        col = col.replace('Low', '↓')
        col = col.replace('SUM', 'Σ')
        return col

    data.columns = [__clean_replace(col) for col in data.columns.values]
    FEATURES = data.columns.values[:-6]
    CLASSES = data.columns.values[-6:]

    # Filter out outlier
    data = data[data['BH↑↓Ratio'] != 0.0]
    data['BH↑↓Ratio'] = (data['BH↑↓Ratio'] - min(data['BH↑↓Ratio'])).astype(int)
    data['BH↑↓Ratio'] = data['BH↑↓Ratio'].apply(lambda x: get_discrete_labels(len(data['BH↑↓Ratio'].unique()))[x])

    # Filter same value columns
    for col in data:
        if len(data[col].unique()) < 2:
            print('Removing column {col} because it has all the same values')
            del data[col]
            if col in FEATURES:
                FEATURES.remove(col)
            if col in CLASSES:
                CLASSES.remove(col)

    # if nb_bins == 2 and strategy == 'median':
    #     for col in FEATURES:
    #         data[col] = 1 * (data[col] > data[col].median())
    #     raise NotImplementedError('Not fully implemented')

    if nb_bins is not False:
        for col in (F for F in FEATURES if F not in ['BH↑↓Ratio']):
            data[col], col_labels = bucketize_into_bins(
                data[col].values,
                nb_bins=min(nb_bins, len(data[col].unique())),
                strategy=strategy,
                retlabels=True,
                label_type='generic'
            )
            data[col] = data[col].apply(lambda x: col_labels[x])
        for col in CLASSES:
            col_labels = get_discrete_labels(2, 'binary')
            data[col] = data[col].apply(lambda x: col_labels[int(x)])

    return data, list(FEATURES), list(CLASSES)


# %%
def load_germancredit(
    main_data_path=PACKAGE_DATA_FOLDER, folder='germancredit', bins=[4, 4, 5], strategy='uniform', raw=False
):
    """
        ____ ____ ____ _  _ ____ _  _ 
        | __ |___ |__/ |\/| |__| |\ | 
        |__] |___ |  \ |  | |  | | \| 


        From UCI ML Repo https://archive.ics.uci.edu/ml/datasets/Statlog+%28German+Credit+Data%29               

        bins: list of int
            - duration
            - amount
            - age
    """

    # Features names list
    GERMAN_FEATURES = [
        'checking', 'duration', 'credit\nhistory', 'purpose', 'amount', 'savings', 'employment', 'installment\nrate',
        'personal\nstatus', 'other\ndebtors', 'residence', 'property', 'age', 'other\ninstallments', 'housing',
        'credits\nnumber', 'job', 'liables\nnumber', 'telephone', 'foreign\nworker', 'class'
    ]

    # Discretized features units
    UNITS = {
        'installment\nrate': '%',
        'liables\nnumber': '',
        'credits\nnumber': '',
        'residence': 'yr.',
        'age': 'yr.',
        'duration': 'mth',
        'amount': 'DM'
    }

    data = pd.read_csv(os.path.join(main_data_path, folder, 'german.data'), sep=' ', header=None)
    data.columns = GERMAN_FEATURES

    if raw:
        return data

    with open(os.path.join(main_data_path, folder, 'german.doc'), 'r') as fp:
        GERMAN_CODES_TO_FEATURES = {
            **{
                GERMAN_FEATURES[i]: {
                    line.strip().split(':')[0].strip(): re.sub(
                        ' +', ' ', ':'.join(line.strip().split(':')[1:]).replace('...', '').replace('..', '').strip()
                    ).replace('<= <', '<=').replace('DM /', 'DM')
                    for line in part.splitlines()[2:] if ':' in line
                } or None
                for i, part in enumerate(re.split('Attribute [0-9]+', fp.read())[1:])
            },
            **{
                'class': {
                    1: 'good',
                    2: 'bad'
                }
            }
        }
#     return GERMAN_CODES_TO_FEATURES

    b = 0
    for col in data.columns.values:
        if GERMAN_CODES_TO_FEATURES[col] is not None:
            #             print(col)
            data[col] = data[col].apply(lambda x: GERMAN_CODES_TO_FEATURES[col][x])
        else:
            if col in ['age', 'amount', 'duration']:
                if bins is not None:
                    data[col], bins_labels = bucketize_into_bins(data[col], bins[b], retlabels=True, strategy=strategy)
                    data[col] = data[col].apply(lambda x: bins_labels[x])
                b += 1
            # else:
            data[col] = data[col].apply(lambda x: str(x) + ' ' + UNITS[col])
            # GERMAN_CODES_TO_FEATURES[col] = {}
    return data


# %%
def load_compas(main_data_path=PACKAGE_DATA_FOLDER, folder='compas'):
    """
        ____ ____ _  _ ___  ____ ____ 
        |    |  | |\/| |__] |__| [__  
        |___ |__| |  | |    |  | ___] 

        From 
            https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm
            https://www.propublica.org/datastore/dataset/compas-recidivism-risk-score-data-and-analysis
            https://github.com/propublica/compas-analysis
                              
    """
    df = pd.read_csv(os.path.join(main_data_path, folder, 'compas-scores-two-years.csv'), index_col='id')
    # Not relevant
    del df['name']
    del df['first']
    del df['last']
    df['age'] = df['age_cat']
    del df['age_cat']  # Alreafy in age
    del df['dob']  # Already in age
    del df['vr_case_number']
    del df['r_case_number']
    del df['c_case_number']
    del df['days_b_screening_arrest']

    # Potentially useless
    del df['c_offense_date']
    del df['c_jail_in']
    del df['c_jail_out']
    del df['event']
    del df['start']
    del df['end']

    # Very partial and potentially useless
    del df['r_days_from_arrest']
    del df['r_jail_in']
    del df['r_jail_out']
    del df['r_offense_date']

    # There is another better cleaned column (and/or less empty)
    del df['r_charge_degree']
    del df['vr_charge_degree']
    del df['r_charge_desc']

    # Almost empty
    del df['vr_offense_date']
    del df['vr_charge_desc']
    del df['c_arrest_date']

    # Empty
    del df['violent_recid']

    # Duplicates
    del df['priors_count.1']

    # Only one unique value
    del df['v_type_of_assessment']
    del df['type_of_assessment']

    # Prediction of COMPAS
    del df['v_decile_score']
    del df['score_text']
    del df['screening_date']
    del df['decile_score.1']
    del df['v_screening_date']
    del df['v_score_text']
    del df['compas_screening_date']
    del df['c_days_from_compas']
    del df['decile_score']

    # Custody
    df = df.dropna()
    df['custody'] = (
        df['out_custody'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d')) -
        df['in_custody'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    ).apply(lambda x: x.total_seconds() / 3600 / 24).astype(int)
    del df['out_custody']
    del df['in_custody']

    def summarise_charge(x):
        drugs = [
            'clonaz', 'heroin', 'cocaine', 'cannabi', 'drug', 'pyrrolidin', 'Methyl', 'MDMA', 'Ethylone', 'Alprazolam',
            'Oxycodone', 'Methadone', 'Methamph', 'Bupren', 'Lorazepam', 'controlled', 'Amphtamine', 'contro',
            'cont sub', 'rapher', 'fluoro', 'ydromor', 'methox', 'iazepa', 'XLR11', 'steroid', 'morphin', 'contr sub',
            'enzylpiper', 'butanediol', 'phentermine', 'Fentanyl', 'Butylone', 'Hydrocodone', 'LSD', 'Amobarbital',
            'Amphetamine', 'Codeine', 'Carisoprodol'
        ]
        drugs_selling = ['sel', 'del', 'traf', 'manuf']
        if sum([d.lower() in x.lower() for d in drugs]) > 0:
            if sum([h in x.lower() for h in drugs_selling]) > 0:
                x = 'Drug Traffic'
            else:
                x = 'Drug Possess'
        elif 'murd' in x.lower() or 'manslaughter' in x.lower():
            x = 'Murder'
        elif 'sex' in x.lower() or 'porn' in x.lower() or 'voy' in x.lower() or 'molest' in x.lower(
        ) or 'exhib' in x.lower():
            x = 'Sex Crime'
        elif 'assault' in x.lower() or 'carjacking' in x.lower():
            x = 'Assault'
        elif 'child' in x.lower() or 'domestic' in x.lower() or 'negle' in x.lower() or 'abuse' in x.lower():
            x = 'Family Crime'
        elif 'batt' in x.lower():
            x = 'Battery'
        elif 'burg' in x.lower() or 'theft' in x.lower() or 'robb' in x.lower() or 'stol' in x.lower():
            x = 'Theft'
        elif 'fraud' in x.lower() or 'forg' in x.lower() or 'laund' in x.lower() or 'countrfeit' in x.lower(
        ) or 'counter' in x.lower() or 'credit' in x.lower():
            x = 'Fraud'
        elif 'prost' in x.lower():
            x = 'Prostitution'
        elif 'trespa' in x.lower() or 'tresspa' in x.lower():
            x = 'Trespass'
        elif 'tamper' in x.lower() or 'fabricat' in x.lower():
            x = 'Tampering'
        elif 'firearm' in x.lower() or 'wep' in x.lower() or 'wea' in x.lower() or 'missil' in x.lower(
        ) or 'shoot' in x.lower():
            x = 'Firearm'
        elif 'alking' in x.lower():
            x = 'Stalking'
        elif 'dama' in x.lower():
            x = 'Damage'
        elif 'driv' in x.lower() or 'road' in x.lower() or 'speed' in x.lower() or 'dui' in x.lower(
        ) or 'd.u.i.' in x.lower():
            x = 'Driving'

        else:
            x = 'Other'

        return x

    df['charge_desc'] = df['c_charge_desc'].apply(summarise_charge)
    del df['c_charge_desc']

    CUSTODY_RANGES = {
        (0, 1):
            '0 days',
        #         (1,2): '1 day',
        #         (2,5): '2-4 days',
        #         (5,10): '5-9 days',
        (1, 10):
            '1-9 days',

        #         (10,30): '10-29 days',
        #         (30,90): '1-3 months',
        #         (90,365): '3-12 months',
        (10, 30):
            '10-29 days',
        (30, 365):
            '1-12 months',

        #         (365,365*2): '1 year',
        #         (365*2,365*3): '2 years',
        (365 * 1, 365 * 3):
            '1-2 years',
        (365 * 3, 365 * 5):
            '3-4 years',
        #         (365*5,365*10): '5-9 years',
        (365 * 5, df['custody'].max() + 1):
            '5 years or more'
        #         (365*10, df['custody'].max()+1): '10 years or more'
    }

    PRIORS_RANGES = {
        (0, 1): '0 priors',
        (1, 2): '1 priors',
        #         (2,3): '2 priors',
        #         (3,5): '3-4 priors',
        (2, 5): '2-4 priors',
        (5, 10): '5-9 priors',
        (10, df['priors_count'].max() + 1): '10 priors or more',
    }
    JUV_OTHER_RANGES = {
        (0, 1): '0 juv others',
        (1, 2): '1 juv others',
        #         (2,3): '2 juv others',
        #         (3,5): '3-4 juv others',
        (2, 5): '2-4 juv others',
        (5, df['juv_other_count'].max() + 1): '5 or more juv others',
    }
    JUV_FEL_RANGES = {
        (0, 1): '0 juv fel',
        (1, 2): '1 juv fel',
        #         (2,3): '2 juv fel',
        #         (3,5): '3-4 juv fel',
        (2, 5): '2-4 juv fel',
        (5, df['juv_fel_count'].max() + 1): '5 or more juv fel',
    }
    JUV_MISD_RANGES = {
        (0, 1): '0 juv misd',
        (1, 2): '1 juv misd',
        #         (2,3): '2 juv misd',
        #         (3,5): '3-4 juv misd',
        (2, 5): '2-4 juv misd',
        (5, df['juv_misd_count'].max() + 1): '5 or more juv misd',
    }

    def get_range(x, RANGES):
        for (a, b), label in RANGES.items():
            if x >= a and x < b:
                return label

    df['custody'] = df['custody'].apply(lambda x: get_range(x, CUSTODY_RANGES))
    df['priors_count'] = df['priors_count'].apply(lambda x: get_range(x, PRIORS_RANGES))
    df['juv_other_count'] = df['juv_other_count'].apply(lambda x: get_range(x, JUV_OTHER_RANGES))
    df['juv_fel_count'] = df['juv_fel_count'].apply(lambda x: get_range(x, JUV_FEL_RANGES))
    df['juv_misd_count'] = df['juv_misd_count'].apply(lambda x: get_range(x, JUV_MISD_RANGES))

    df['is_recid'] = df['is_violent_recid'].apply(lambda x: 'Yes' if x == 1 else 'No')
    df['is_violent_recid'] = df['is_violent_recid'].apply(lambda x: 'Yes' if x == 1 else 'No')
    df['two_year_recid'] = df['two_year_recid'].apply(lambda x: 'Yes' if x == 1 else 'No')
    df['charge_degree'] = df['c_charge_degree'].apply(lambda x: 'Felony' if x == 'F' else 'Misdemeanor')
    del df['c_charge_degree']

    # df['custody'], custody_bins = pd.cut(df['custody'], bins = 10, labels = False, retbins = True)
    # df['priors_count'], custody_bins = pd.cut(df['10'], bins = 10, labels = False, retbins = True)
    print(f'Loaded {len(df)} records')

    df = pd.concat([df[[col for col in df.columns.values if col != 'two_year_recid']], df[['two_year_recid']]], axis=1)
    return df


# #### Additional information in COMPAS
# Information about the marital status might be extracted from the database

# import sqlite3
# # Create your connection.
# con = sqlite3.connect('../data/compas/compas.db')

# cursor = con.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor.fetchall())

# status = {row['compas_person_id']: row['marital_status'] for r, row in pd.read_sql_query("SELECT * from compas", con).iterrows()}

# pd.read_sql_query("SELECT * from compas", con)


# %%
def load_car(main_data_path, folder='car', df=None):
    """
    ____ ____ ____ 
    |    |__| |__/ 
    |___ |  | |  \ 

    From UCI ML Repo https://archive.ics.uci.edu/ml/datasets/Car+Evaluation               
    """

    df = pd.read_csv(os.path.join(main_data_path, folder, 'car.data'), header=None)
    for col in df:
        df[col] = df[col].apply(
            lambda x: x.replace('vhigh', 'very high').replace('med', 'medium').replace('more', '5 or more').
            replace('55', '5').replace('vgood', 'very good').replace('acc', 'acceptable')
        )
    df.columns = [
        'buying\ncost', 'maintenance\ncost', 'doors\nnumber', 'persons\nnumber', 'trunk\nsize', 'safety', 'score'
    ]
    return df, 'score'


# %%
def load_cmc(main_data_path, folder='contraccettivi', bins=[10], df=None):
    """"
    ____ ____ _  _ ___ ____ ____ ____ ____ ___  ___ _ _  _ ____ 
    |    |  | |\ |  |  |__/ |__| |    |___ |__]  |  | |  | |___ 
    |___ |__| | \|  |  |  \ |  | |___ |___ |     |  |  \/  |___ 
                                                                

    From UCI  (Contraceptive Method Choice, CMC)
        https://archive.ics.uci.edu/ml/datasets/Contraceptive+Method+Choice

    bins : list of int
        - wife age
    """

    # Decoder
    decoder_cmc = [
        [], [None, 'Level 1 (Lowest)', 'Level 2', 'Level 3', 'Level 4 (Highest)'],
        [None, 'Level 1 (Lowest)', 'Level 2', 'Level 3', 'Level 4 (Highest)'], ['0', '1', '2', '3', '4', '5 or more'],
        ['Others', 'Islam'], ['Working', 'Unemployed'], [None, 'Job 1', 'Job 2', 'Job 3', 'Job 4'],
        [None, 'Low', 'Medium-Low', 'Medium-High', 'High'], ['Good', 'Not Good'],
        [None, 'No use', 'Long-term', 'Short-term']
    ]

    # Child nb.
    def child_cat(nb):
        if nb <= 4:
            return int(nb)
        else:
            return 5

    df = pd.read_csv(os.path.join(main_data_path, folder, 'cmc.data'), header=None)
    df.columns = [
        'Wife\'s\nAge', 'Wife\'s\nEducation', 'Husband\'s\nEducation', 'Number of\nChildren', 'Wife\'s\nReligion',
        ' Wife\'s\nOccupation', 'Husband\'s\nOccupation', 'Living\nStandard', 'Media Exposure',
        'Contraceptive Method Used'
    ]
    df['Wife\'s\nAge'], age_labels = bucketize_into_bins(
        df['Wife\'s\nAge'].values, bins[0], retlabels=True, label_unit='yr.', round_label=0, strategy='quantile'
    )
    df['Number of\nChildren'] = df['Number of\nChildren'].apply(child_cat)
    decoder_cmc[0] = age_labels
    for c, col in enumerate(df):
        df[col] = df[col].apply(lambda x: decoder_cmc[c][x])
    return df, df.columns.values[-1]


# %%


def load_shuttle(main_data_path, folder='shuttle', df=None):
    """
    ____ _  _ _  _ ___ ___ _    ____ 
    [__  |__| |  |  |   |  |    |___ 
    ___] |  | |__|  |   |  |___ |___ 

    From UCI https://archive.ics.uci.edu/ml/datasets/Shuttle+Landing+Control
                                 
    """
    # Encoder
    encoder_shuttle = [
        list(range(1, 3)),
        list(range(1, 3)),
        list(range(1, 5)),
        list(range(1, 3)),
        list(range(1, 3)),
        list(range(1, 5)),
        list(range(1, 3))
    ]

    # Columns names
    shuttle_columns = [
        'Recommended\nControl Mode', 'Positioning', 'Altimeter Error\nMagnitude', 'Altimeter Error\nSign',
        'Wind\nDirection', 'Wind\nStrength', 'Sky Condition'
    ]

    # Decoder
    shuttle_decoder = [
        ['Manual', 'Automatic'], ['Stable', 'Unstable'], ['Very Large', 'Large', 'Medium', 'Small'],
        ['Positive', 'Negative'], ['Head', 'Tail'], ['Light', 'Medium', 'Strong', 'Very Strong'],
        ['Good Visibility', 'No Visibility']
    ]

    def combinatorial_from_record(record):
        """
            Generate the combinatorial rows for missing ones
            i.e. if * is present in a record it generates all the possible combinations for that column

            (works on dicts, it's easier than pd.DataFrame)
        """
        combi = [k for k, v in record.items() if v == '*']
        non_combi = [k for k, v in record.items() if v != '*']
        if len(combi) > 0:
            combi_mesh_start = [encoder_shuttle[i] for i in combi]
            combi_cols = np.array(np.meshgrid(*combi_mesh_start)).T.reshape(-1, len(combi_mesh_start))
            retds = []
            for cs in combi_cols:
                retds.append({**{k: int(record[k]) for k in non_combi}, **{k: int(c) for k, c in zip(combi, cs)}})
            return retds
        else:
            return [{k: int(v) for k, v in record.items()}]

    df_raw = pd.read_csv(os.path.join(main_data_path, folder, 'shuttle-landing-control.data'), header=None)
    df = pd.DataFrame(sum([combinatorial_from_record(record) for record in df_raw.to_dict('records')], []))
    for col in df:
        df[col] = df[col].apply(lambda x: shuttle_decoder[col][x - 1])
    df.columns = [shuttle_columns[col] for col in df]
    df = df[[shuttle_columns[i] for i in [0, 1, -2, -3, -1, 2, 3]]]
    return df, df.columns.values[0]


# %%


def load_give_me_some_credit(
    folder=os.path.join(PACKAGE_DATA_FOLDER, 'givemesomecredit'), cleaning_type='top_perc,remove_non_monotone'
):
    """
        Credit: The preprocessing was taken from https://www.kaggle.com/leafar/give-me-some-credit

        Note: test data do not have any label.

    """
    def cleaned_dataset(dataset):
        dataset.loc[dataset["age"] <= 18, "age"] = dataset.age.median()

        age_working = dataset.loc[(dataset["age"] >= 18) & (dataset["age"] < 60)]
        age_senior = dataset.loc[(dataset["age"] >= 60)]

        age_working_impute = age_working.MonthlyIncome.mean()
        age_senior_impute = age_senior.MonthlyIncome.mean()

        dataset["MonthlyIncome"] = np.absolute(dataset["MonthlyIncome"])
        dataset["MonthlyIncome"] = dataset["MonthlyIncome"].fillna(99999)
        dataset["MonthlyIncome"] = dataset["MonthlyIncome"].astype('int64')

        dataset.loc[((dataset["age"] >= 18) & (dataset["age"] < 60)) & (dataset["MonthlyIncome"] == 99999),
                    "MonthlyIncome"] = age_working_impute
        dataset.loc[(train_data["age"] >= 60) & (dataset["MonthlyIncome"] == 99999),
                    "MonthlyIncome"] = age_senior_impute
        dataset["NumberOfDependents"] = np.absolute(dataset["NumberOfDependents"])
        dataset["NumberOfDependents"] = dataset["NumberOfDependents"].fillna(0)
        dataset["NumberOfDependents"] = dataset["NumberOfDependents"].astype('int64')

        dataset["CombinedDefaulted"] = \
            dataset["NumberOfTimes90DaysLate"] + dataset["NumberOfTime60-89DaysPastDueNotWorse"] + \
            dataset["NumberOfTime30-59DaysPastDueNotWorse"]

        dataset.loc[(dataset["CombinedDefaulted"] >= 1), "CombinedDefaulted"] = 1

        dataset["CombinedCreditLoans"] = \
            dataset["NumberOfOpenCreditLinesAndLoans"] + dataset["NumberRealEstateLoansOrLines"]
        dataset.loc[(dataset["CombinedCreditLoans"] <= 5), "CombinedCreditLoans"] = 0
        dataset.loc[(dataset["CombinedCreditLoans"] > 5), "CombinedCreditLoans"] = 1

        dataset.drop(
            [
                "Unnamed: 0",
                "NumberOfOpenCreditLinesAndLoans",
                "NumberOfTimes90DaysLate",
                "NumberRealEstateLoansOrLines",
                "NumberOfTime60-89DaysPastDueNotWorse",
            ],
            axis=1,
            inplace=True
        )

        return dataset

    COLS_TOBE_TOP_PERC_CLEANED = [
        'RevolvingUtilizationOfUnsecuredLines', 'DebtRatio', 'MonthlyIncome', 'NumberOfTime30-59DaysPastDueNotWorse'
    ]
    limits = [None] * len(COLS_TOBE_TOP_PERC_CLEANED)

    def top_percentile_cleaning(df):
        ldf = len(df)
        for i, (c, l) in enumerate(zip(COLS_TOBE_TOP_PERC_CLEANED, list(limits))):
            if l is None:
                limits[i] = df.sort_values([c]).tail(int(ldf * .01)).iloc[0][c]
            df = df[df[c] < limits[i]]

        return df.reset_index(drop=True).copy()

    def remove_non_monotone(df):
        df.drop(columns=['DebtRatio'], inplace=True)
        return df

    # Load the dataframes
    train_data = pd.read_csv(os.path.join(folder, 'cs-training.csv'))
    test_data = pd.read_csv(os.path.join(folder, 'cs-test.csv'))

    # Clean the data
    train_data = cleaned_dataset(train_data)
    test_data = cleaned_dataset(test_data)

    if 'top_perc' in cleaning_type:
        train_data = top_percentile_cleaning(train_data)
        test_data = top_percentile_cleaning(test_data)

    if 'remove_non_monotone' in cleaning_type:
        train_data = remove_non_monotone(train_data)
        test_data = remove_non_monotone(test_data)

    return BaseAttrDict(
        data=train_data.reset_index(drop=True).copy(),
        test_data=test_data.reset_index(drop=True).copy(),
        target_name='SeriousDlqin2yrs',
        class_names=['Good', 'Bad'],
    )


# %%


def load_winequality(
    folder=os.path.join(PACKAGE_DATA_FOLDER, 'winequality'),
    type='white',
    red_filename='winequality-red.csv',
    white_filename='winequality-white.csv',
    binary_target_threshold=None,
):

    if type == 'white':
        filename = white_filename
    elif type == 'red':
        filename = red_filename
    else:
        raise ValueError('Invalid type. It must be either \'red\' or \'white\'')

    data = pd.read_csv(os.path.join(folder, filename), sep=';')

    if binary_target_threshold is not None:
        data['quality'] = data['quality'].apply(lambda x: (x < binary_target_threshold) * 1)
        class_names = ['Bad', 'Good']
    else:
        data['quality'] = data['quality'] - 3
        class_names = [str(x) for x in np.sort(data['quality'].unique())]

    return BaseAttrDict(data=data, target_name='quality', class_names=class_names)


# %%
