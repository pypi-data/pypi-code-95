import numpy as np
import pandas as pd
from aimltools.ts.distances import tsdist
from aimltools.ts.denoising import denoise
import tslearn.barycenters
from scipy import stats
import logging
from deprecation import deprecated
from abc import ABCMeta, abstractmethod
from PyNomaly import loop


from pyod.models.lscp import LSCP
from pyod.models.lof import LOF
from pyod.models.feature_bagging import FeatureBagging
from pyod.models.pca import PCA
from pyod.models.auto_encoder import AutoEncoder
from keras import backend as K

logger = logging.getLogger(__name__)


class ClassifierBaseMixin(metaclass = ABCMeta):

    """
    Mixin class containing functionality specific to
    classifiers

    Also contains abstract methods
    """
    
    @abstractmethod
    def fit(self, X, y):
        """
        Method to fit a model from training data
        Mandatorily implement this method in all child mixins
        """
        
    @abstractmethod
    def predict(self, X_new):
        """
        Method to predict labels after classification on new data 
        from a trained model
        Mandatorily implement this method in all child mixins
        """
        
    @abstractmethod
    def predict_proba(self, X_new):
        """
        Method to predict probability scores of classification on new data 
        from a trained model
        Mandatorily implement this method in all child mixins"""


class LOOPClassifier(ClassifierBaseMixin):
    
    """
    Class that implements classification based on the Local Outlier Probabilities (LoOP)
    method, the implementation of which is taken from the PyNomaly library - 
    (https://github.com/vc1492a/PyNomaly)
    """

    def __repr__(self):
        return """LOOP classifier\n
            Arguments: n_neighbors={}, threshold={}, use_numba={}
        """.format(self.__n_neighbors, self.__threshold, self.__use_numba)
    
    def __init__(self, n_neighbors=10, use_numba=True, threshold = 0.5):
        self.__n_neighbors = n_neighbors
        self.__use_numba = use_numba
        self.__threshold = threshold    
    
    def fit(self, X):
        try:
            self.model = loop.LocalOutlierProbability(X, n_neighbors=self.__n_neighbors, use_numba=self.__use_numba)        
            self.model.fit()
        except Exception as error:
            logger.error("Error while training using PyNomaly.loop: {}".format(error))

    def predict(self, X):
        try:
            probs = self.predict_proba(X)
            preds = []
            for p in probs:
                res = 1 if p > self.__threshold else 0
                preds.append(res)
            return np.array(preds)
        except Exception as error:
            logger.error("Error while prediction using PyNomaly.loop: {}".format(error))
    
    def predict_proba(self, X):
        try:
            probs = []
            if (type(X) is pd.core.frame.DataFrame): 
                for itpl in X.itertuples():
                    score = self.model.stream(np.array(itpl)[1:])
                    probs.append(score)
            elif (type(X) is np.ndarray):
                for i in range(0,len(X)):
                    score = self.model.stream(X[i])
                    probs.append(score)
                    
            return np.array(probs)
        except Exception as error:
            logger.error("Error while predicting probabilities using PyNomaly.loop: {}".format(error))
            

class PyODClassifier(ClassifierBaseMixin):
    """
    Class that implements classification based on models that are part of the PyOD library
    """
    @abstractmethod
    def __repr__(self):
        """
        Mandatorily implement this method in all child classes
        """
    
    def __init__(self):
        self._model = {"NA"}
        
    @abstractmethod
    def fit(self, X):
        """
        Mandatorily implement this method in all child classes
        """
        
    def predict(self, X):
        try:
            preds = self._model.predict(X)
            return preds
        except Exception as error:
            logger.error("Error while predicting using {} ({})".format(self._model, error))
            
    def predict_proba(self, X):
        try:
            probs = self._model.predict_proba(X)[:,1]
            return probs 
        except Exception as error:
            logger.error("Error while predicting probabilities using {} ({})".format(self._model, error))
            

class ANNClassifier(PyODClassifier):
    """
    Class that implements classification based on AutoEncoder NN
    method, the implementation of which is taken from the PyOD library
    """
    
    def __repr__(self):
        return "AutoEncoder NN classifier.\n{}".format(self._model)
    
    def __init__(self, outliers_fraction = 0.001, epochs = 30, hidden_neurons = [], reset_keras_before_fit = True):
        super().__init__()
        self.__outliers_fraction = outliers_fraction
        self.__epochs = epochs
        self.__hidden_neurons = hidden_neurons
        self.__reset_keras_before_fit = reset_keras_before_fit
        self.__random_state = None
    
    def set_hidden_neurons(self, hidden_neurons):
        self.__hidden_neurons = hidden_neurons

    def reset_keras_before_fit(self, reset_keras_after_fit):
        self.__reset_keras_before_fit = reset_keras_after_fit

    def set_random_state(self, random_state):
        self.__random_state = random_state

    def fit(self, X):
        if len(self.__hidden_neurons) == 0:
            try:
                self.__hidden_neurons = [len(X.columns)-1]
            except Exception as error:
                self.__hidden_neurons = [len(X[0])]
        
        try:
            if self.__reset_keras_before_fit:
                K.clear_session()
            self._model = AutoEncoder(epochs=self.__epochs, hidden_neurons=self.__hidden_neurons, contamination=self.__outliers_fraction, verbose = 0, random_state=self.__random_state)
            self._model.fit(X)
        except Exception as error:
            logger.error("Error while training using PyOD.AutoEncoder: {}".format(error))
            
            
class LSCPClassifier(PyODClassifier):
    """
    Class that implements classification based on the Locally Selective Combination of Parallel Outlier Ensembles
    method, the implementation of which is taken from the PyOD library
    """

    def __repr__(self):
        return "LSCP classifier.\n{}".format(self._model)
    
    def __init__(self, threshold = 0.5, detector_list = [LOF(n_neighbors=5), LOF(n_neighbors=10), LOF(n_neighbors=15),
                 LOF(n_neighbors=20), LOF(n_neighbors=25), LOF(n_neighbors=30),
                 LOF(n_neighbors=35), LOF(n_neighbors=40), LOF(n_neighbors=45),
                 LOF(n_neighbors=50)]):
        super().__init__()
        self.__threshold = threshold
        self.__detector_list = detector_list
        
    def fit(self, X):
        try:
            self._model = LSCP(self.__detector_list, random_state=42)
            self._model.fit(X)
        except Exception as error:
            logger.error("Error while training with PyOD.LSCPClassifier: {}".format(error))
            

class FeatureBaggingClassifier(PyODClassifier):
    """
    Class that implements classification based on Feature bagging
    method, the implementation of which is taken from the PyOD library
    """
    
    def __repr__(self):
        return "Feature bagging classifier.\n{}".format(self._model)
    
    def __init__(self, check_estimator=False):
        super().__init__()
        self.__check_estimator = check_estimator
    
    def fit(self, X):
        try:
            self._model = FeatureBagging(check_estimator = self.__check_estimator)
            self._model.fit(X)
        except Exception as error:
            logger.error("Error while training with PyOD.FeatureBaggingClassifier: {}".format(error))
            

class PCAClassifier(PyODClassifier):
    """
    Class that implements classification based on Principal Component Analysis (PCA)
    method, the implementation of which is taken from the PyOD library
    """
    
    def __repr__(self):
        return "Principal Component Analysis (PCA) classifier.\n{}".format(self._model)
    
    def __init__(self, outliers_fraction = 0.001):
        super().__init__()
        self.__outliers_fraction = outliers_fraction
    
    def fit(self, X):
        try:
            self._model = PCA(contamination=self.__outliers_fraction, random_state=1)
            self._model.fit(X)
        except Exception as error:
            logger.error("Error while training with PyOD.PCA: {}".format(error))
            

@deprecated(deprecated_in="0.7.0", removed_in="0.8.0")
class PercentileClassifier(ClassifierBaseMixin):

    """
    Class that implements classification using an 
    arbitrarily defined percentile value
    """

    def fit(self, X, cutoff_quantile, tag, reference_cycle, distance_type):
    
        self.tag = tag
        self.reference_cycle = reference_cycle
        self.distance_type = distance_type
        
        self.ref_ts = np.array(X[(X.tag == self.tag) & (X.cycle == self.reference_cycle)].value)
        df_ts = X[(X.tag == self.tag) & (X.cycle != self.reference_cycle)]
        self.distances = calculate_distances(df_ts, self.ref_ts, distance_type)
        self.quant_value = np.quantile(list(self.distances.values()), cutoff_quantile)
    
    
    def predict(self, X):
        
        df = X[(X.tag == self.tag)]    
        self.distances = calculate_distances(df, self.ref_ts, distance_type=self.distance_type)
        self.cycles = []
        self.pred_labels = []
    
        for key, value in self.distances.items():
            self.cycles.append(key)
            if value > self.quant_value:
                self.pred_labels.append(1)
            else:
                self.pred_labels.append(0)
                
        return self.pred_labels
    
    def predict_proba(self, X):
        raise NotImplementedError("Model is not probabilistic")

@deprecated(deprecated_in="0.7.0", removed_in="0.8.0")        
class KDEClassifier(ClassifierBaseMixin):
    
    """
    Class that implements classification using an 
    kernel density estimation on training data and an
    arbitrary threshold value
    """

    def fit(self, X, threshold, tag, reference_cycle, distance_type):
        
        self.tag = tag
        self.reference_cycle = reference_cycle
        self.distance_type = distance_type
        self.threshold = 1 - threshold
        
        self.ref_ts = np.array(X[(X.tag == self.tag) & (X.cycle == self.reference_cycle)].value)
        df_ts = X[(X.tag == self.tag) & (X.cycle != self.reference_cycle)]
        distances = calculate_distances(df_ts, self.ref_ts, distance_type)
        
        self.sample_pdf = stats.gaussian_kde(list(distances.values()))

        
    def predict(self, X):
    
        df = X[(X.tag == self.tag)]
        self.distances = calculate_distances(df, self.ref_ts, distance_type=self.distance_type)
        self.cycles = []
        self.probs = []
        self.pred_labels = []
        
        for key, value in self.distances.items():
            
            self.cycles.append(key)
            prob = self.sample_pdf.integrate_box_1d(value, max(self.distances.values()))
            self.probs.append(prob)
            
            if prob < self.threshold:
                self.pred_labels.append(1)
            else:
                self.pred_labels.append(0)
                
        return self.pred_labels
    
    def predict_proba(self, X):
        return self.probs
    
@deprecated(deprecated_in="0.7.0", removed_in="0.8.0")
class ClassifierBaseClass(metaclass = ABCMeta):

    def __init__(self, X, classifier, **kwargs):
        self.X = X
        self.classifier = classifier
        self.kwargs = kwargs
    
    def __repr__(self):
        return """Classification method = {}, \n
            Arguments = {}""".format(self.classifier, self.kwargs)

    @abstractmethod
    def classify(self):
        """
        Mandatorily implement this method in all child classes
        """

@deprecated(deprecated_in="0.7.0", removed_in="0.8.0")
def calculate_distances(df_ts, ref_ts, distance_type="sdtw"):

    """
    Function to calculate distances between a reference signal
    and multiple other signals

    Documentation to be written
    """

    cycle_list = df_ts.cycle.unique()
    distances_dict = {}
    for cycle_n in cycle_list:
        ts = df_ts[df_ts.cycle == cycle_n].value
        d = tsdist(ts, ref_ts, distance_type=distance_type)
        distances_dict[cycle_n] = d
    return distances_dict
    
@deprecated(deprecated_in="0.7.0", removed_in="0.8.0")
def calculate_barycenter(df_ts, apply_denoise = False):

    """
    Function to compute barycenter of multiple signals

    Documentation to be written
    """

    cycle_list = df_ts.cycle.unique()
    ts_list = []
    for cycle_n in cycle_list:
        ts = df_ts[df_ts.cycle == cycle_n].value
        if apply_denoise == True:
            ts = denoise(ts, denoise_type='wavelet', level = None, 
            threshold = 0.7, axis = -1, wavedec_mode = 'symmetric', 
            return_noise=False, threshold_mode='soft')
        ts_list.append(ts)
    return tslearn.barycenters.dtw_barycenter_averaging(ts_list, max_iter=50, tol=1e-3)

@deprecated(deprecated_in="0.7.0", removed_in="0.8.0")
def insert_cycle(df_ts, value_new_cycle, tag):

    """
    Function to insert a new cycle into a dataframe containing
    data on existing cycles

    Documentation to be written
    """
    
    ts = time.gmtime()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
    
    value = value_new_cycle
    cycles = df_ts.cycle
    new_cycle_num = max(cycles) + 1
    
    assert new_cycle_num not in cycles
    
    df_new_cycle = pd.DataFrame(value, columns=["value"])
    
    df_new_cycle['time'] = timestamp
    df_new_cycle['cycle'] = new_cycle_num
    df_new_cycle['tag'] = tag
    
    df_ts = pd.concat([df_ts, df_new_cycle], axis=0, sort=False)
    df_ts.reset_index(inplace=True)
    
    return df_ts