from .IO import read as _read
from .QC import qc as _qc
from .normalization import normalize as _normalize
from .imputation import impute as _impute
from .reshaping import reshape as _reshape
from .modeling import buildmodel as _buildmodel
from .interpretation import explain as _explain
import pandas as pd
import numpy as np
import torch


try:
    from captum.attr import visualization as viz
except:
    import sys
    print("The module 'captum' is not found, please install first.")
    print("\tconda install captum -c pytorch")
    sys.exit(0)

def _is_df(a):
    return True if type(a) is pd.DataFrame else False

def dataset_split(dataset, labels, train_proportion=0.7):
    n_all = len(labels)
    n_select = round(n_all * train_proportion)
    idx_all = range(n_all)
    idx_train = np.random.choice(n_all, size=n_select, replace=False)
    idx_test = list(set(idx_all) - set(idx_train))
    return dataset[idx_train], labels[idx_train], dataset[idx_test], labels[idx_test], idx_test

class MData:
    def __init__(self):
        self.full_data = None
        self.train_data = None
        self.test_data = None
        self.full_X = None
        self.full_y = None
        self.train_X = None
        self.train_y = None
        self.test_X = None
        self.test_y = None
        self.model = None
        self.attributions = None
        self.features = None
        self.num2label = {}
        self.label2num = {}
        self.importances = None
        self.full_y_sample_id = None
        self.test_y_sample_id = None

    def __repr__(self) -> str:
        if _is_df(self.full_data):
            print(self.full_data)
            return str(self.full_data.shape)
        if _is_df(self.train_data):
            print(self.train_data)
            if _is_df(self.test_data):
                print(self.test_data)
                return 'Train: '+str(self.train_data.shape)+'; Test: '+str(self.test_data.shape)
        return '0'

    def read(self, fname, role='all', group_col='Group'):
        if role=='all':
            self.full_data = _read(fname)
            self.full_y = self.full_data[group_col]
            self.full_X = self.full_data.drop(columns=group_col)
            self.full_data = self.full_data
        elif role=='train':
            self.train_data = _read(fname)
            self.train_y = self.train_data[group_col]
            self.train_X = self.train_data.drop(columns=group_col)
            self.train_data = self.train_data
        elif role=='test':
            self.test_data = _read(fname)
            self.test_y = self.test_data[group_col]
            self.test_X = self.test_data.drop(columns=group_col)
            self.test_data = self.test_data
        else:
            print(f"Illegal role: {role}!")
    
    def qc(self, obs=0.3):
        bf, af = 0, 0
        if _is_df(self.full_data):
            bf = len(list(self.full_X))
            self.full_X = _qc(self.full_X, obs)
            af = len(list(self.full_X))
        if _is_df(self.train_data):
            if _is_df(self.test_data):
                combined_X = pd.concat([self.train_X, self.test_X], sort=False)
                bf = len(list(combined_X))
                combined_X = _qc(combined_X, obs)
                af = len(list(combined_X))
                self.train_X = combined_X.loc[self.train_y.index,:]
                self.test_X = combined_X.loc[self.test_y.index,:]
        print(f'Number of features: from {bf} to {af}.')
    
    def normalize(self, method='log2p'):
        if _is_df(self.full_data):
            self.full_X = _normalize(self.full_X, method)
        if _is_df(self.train_data):
            if _is_df(self.test_data):
                self.train_X = _normalize(self.train_X, method)
                self.test_X = _normalize(self.test_X, method)
    
    def impute(self, method='none'):
        if _is_df(self.full_data):
            self.full_X = _impute(self.full_X, method)
        if _is_df(self.train_data):
            if _is_df(self.test_data):
                self.train_X = _impute(self.train_X, method)
                self.test_X = _impute(self.test_X, method)
    
    def reshape(self, method='auto', train_proportion=0.7):
        if _is_df(self.full_data):
            full_X, self.features = _reshape(self.full_X, method)
            uniq_label = list(set(self.full_y))
            self.full_y_sample_id = self.full_y.index
            self.full_y = np.array([uniq_label.index(i) for i in self.full_y])
            for i, v in enumerate(uniq_label):
                self.num2label[i] = v
                self.label2num[v] = i
            self.train_X, self.train_y, self.test_X, self.test_y, test_sample_index = dataset_split(full_X, self.full_y, train_proportion)
            self.test_y_sample_id = self.full_y_sample_id[test_sample_index]
        if _is_df(self.train_data):
            if _is_df(self.test_data):
                self.train_X, self.features = _reshape(self.train_X, method)
                self.test_X, self.features = _reshape(self.test_X, method)
                self.test_y_sample_id = self.test_y.index
                uniq_label = list(set(self.train_y))
                self.train_y = np.array([uniq_label.index(i) for i in self.train_y])
                self.test_y = np.array([uniq_label.index(i) for i in self.test_y])
                for i, v in enumerate(uniq_label):
                    self.num2label[i] = v
                    self.label2num[v] = i
    
    def buildmodel(self, method='default', epochs=5):
        self.model = _buildmodel(self.train_X, self.train_y, self.test_X, self.test_y, method, self.train_X.shape[-1], len(self.num2label), epochs)
    
    def explain(self, target, method='IntegratedGradients'):
        if type(self.model) is not None:
            self.attributions = _explain(self.model, self.test_X, method, target=self.label2num[target])
        attr = self.attributions.numpy()
        n_sample, n_width = attr.shape[0], attr.shape[-1]
        attr = attr.reshape(n_sample, n_width**2)
        imp = pd.DataFrame(data=attr, index=self.test_y_sample_id, columns=self.features)
        self.importances = imp
        cols = imp.apply(np.mean).abs().sort_values(ascending=False).head(20).index
        imp[cols].apply(np.mean).plot.bar().get_figure().savefig('TOP20_KeyFeatures.png', dpi=300)

    def save(self):
        self.importances.to_csv('FeatureImportance.tsv', sep='\t')
        attr_ig = np.transpose(self.attributions.squeeze().cpu().detach().numpy(), (1,2,0))
        viz.visualize_image_attr(attr_ig, sign="all", cmap="viridis", show_colorbar=True, title="", alpha_overlay=1)[0].savefig('FeatureImportances.png', dpi=300)
    