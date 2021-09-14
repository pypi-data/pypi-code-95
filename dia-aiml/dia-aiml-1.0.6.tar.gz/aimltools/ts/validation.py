import numpy as np
from aimltools.ts import DataPreparation
from collections import Counter, OrderedDict
import logging

logger = logging.getLogger(__name__)


class AnomalyDetectionValidation:
    
    def __init__(self):
        self.__TXT_HYPER_FLD = 'hyperparameters'
        self.__TXT_CLASSIFIER_FLD = 'classifier'

        self.__TXT_ACC = "accuracy (tp+tn/(tp+tn+fp+fn))"
        self.__TXT_TRUEN = "true negative rate (tn/(tn+fp))"
        self.__TXT_NEGATIVEPV = "negative pred. value (tn/(tn+fn))"
        self.__TXT_F1SCORE = "f1 score (2*(P*R)/(P+R))"
        self.__TXT_RECALL = "recall (tp/(tp+fn))"
        self.__TXT_PREC = "precision (tp/(tp+fp))"
        self.__TXT_FN = "anomalous detected as normal (false negatives)"
        self.__TXT_TP = "anomalous detected as anomalous (true positives)"
        self.__TXT_FP = "normal detected as anomalous (false positives)"
        self.__TXT_TN = "normal detected as normal (true negatives)"
        self.__TXT_ACC_WP = "accuracy - with perturbations"
        self.__TXT_ACC_NP = "accuracy - no perturbations"
        self.__TXT_CNT_WP = "count - with perturbations"
        self.__TXT_CNT_NP = "count - no perturbations"
        self.__TXT_SCORE_WP = "score - with perturbations"
        self.__TXT_SCORE_NP = "score - no perturbations"
        self.__TXT_PRED_WP = "pred - with perturbations"
        self.__TXT_PRED_NP = "pred - no perturbations"
        self.__TXT_MODEL = 'model'
    
    def get_fn(self):
        return self.__results[self.__TXT_FN]
    
    def get_tp(self):
        return self.__results[self.__TXT_TP]
    
    def get_fp(self):
        return self.__results[self.__TXT_FP]
    
    def get_tn(self):
        return self.__results[self.__TXT_TN]
    
    def get_precision(self):
        try:
            return self.__results[self.__TXT_TP] / (self.__results[self.__TXT_TP] + self.__results[self.__TXT_FP])
        except:
            logger.error("Cannot calculate {}: {} and {} are both zero".format(self.__TXT_PREC, self.__TXT_TP, self.__TXT_FP))
            return np.nan


    def get_recall(self):
        try:
            return self.__results[self.__TXT_TP] / (self.__results[self.__TXT_TP] + self.__results[self.__TXT_FN])
        except:
            logger.error("Cannot calculate {}: {} and {} are both zero".format(self.__TXT_RECALL, self.__TXT_TP, self.__TXT_FN))
            return np.nan


    def get_specificity(self):
        try:
            return self.__results[self.__TXT_TN] / (self.__results[self.__TXT_TN] + self.__results[self.__TXT_FP])
        except:
            logger.error("Cannot calculate {}: {} and {} are both zero".format(self.__TXT_TRUEN, self.__TXT_TN, self.__TXT_FP))
            return np.nan
    
    
    def get_negativepv(self):
        try:
            return self.__results[self.__TXT_TN] / (self.__results[self.__TXT_TN] + self.__results[self.__TXT_FN])
        except:
            logger.error("Cannot calculate {}: {} and {} are both zero".format(self.__TXT_NEGATIVEPV, self.__TXT_TN, self.__TXT_FN))
            return np.nan
    
    
    def get_f1score(self):
        p = self.get_precision()
        r = self.get_recall()
        try:
            return 2*(p*r)/(p+r)
        except:
            logger.error("Cannot calculate {}: {} and {} are both zero".format(self.__TXT_F1SCORE, self.__TXT_PREC, self.__TXT_RECALL))
            return np.nan
    
    
    def get_accuracy(self):
        t = self.__results[self.__TXT_TP] + self.__results[self.__TXT_TN]
        f = self.__results[self.__TXT_FP] + self.__results[self.__TXT_FN]
        try:
            return t/(t+f)
        except:
            logger.error("Cannot calculate {}: division by zero".format(self.__TXT_ACC))
            return np.nan


    @staticmethod
    def __count(preds, preds_perturb):
        cnt = dict(Counter(preds))
        cnt_perturbed = dict(Counter(preds_perturb))
        
        for i in [0, 1]:
            if not (i in cnt.keys()):
                cnt[i] = 0
            if not (i in cnt_perturbed.keys()):
                cnt_perturbed[i] = 0
        
        cnt = OrderedDict(sorted(cnt.items()))
        cnt_perturbed = OrderedDict(sorted(cnt_perturbed.items()))
        return [cnt, cnt_perturbed]
    
    
    def __create_result_dict(self, model_name, preds, preds_proba, preds_perturb, preds_proba_perturb):
        [cnt, cnt_perturbed] = AnomalyDetectionValidation.__count(preds, preds_perturb)
        
        self.__results = {}
        self.__results[self.__TXT_MODEL] = model_name
        self.__results[self.__TXT_PRED_NP] = preds
        self.__results[self.__TXT_PRED_WP] = preds_perturb
        self.__results[self.__TXT_SCORE_NP] = preds_proba
        self.__results[self.__TXT_SCORE_WP] = preds_proba_perturb
        self.__results[self.__TXT_CNT_NP] = cnt
        self.__results[self.__TXT_CNT_WP] = cnt_perturbed
        #self.__results[self.__TXT_ACC_NP] = cnt[0] / sum(cnt.values())
        #self.__results[self.__TXT_ACC_WP] = cnt_perturbed[1] / sum(cnt_perturbed.values())
        self.__results[self.__TXT_TN] = cnt[0]
        self.__results[self.__TXT_FP] = cnt[1]
        self.__results[self.__TXT_TP] = cnt_perturbed[1]
        self.__results[self.__TXT_FN] = cnt_perturbed[0]
        
        self.__results[self.__TXT_ACC] = self.get_accuracy()
        self.__results[self.__TXT_PREC] = self.get_precision()
        self.__results[self.__TXT_RECALL] = self.get_recall()
        self.__results[self.__TXT_TRUEN] = self.get_specificity()
        self.__results[self.__TXT_NEGATIVEPV] = self.get_negativepv()
        self.__results[self.__TXT_F1SCORE] = self.get_f1score()
        
    
    def get_results_summary(self):
        summary = self.__results.copy()
        summary.pop(self.__TXT_PRED_NP, None)
        summary.pop(self.__TXT_PRED_WP, None)
        summary.pop(self.__TXT_SCORE_NP, None)
        summary.pop(self.__TXT_SCORE_WP, None)
        return summary
        
    
    def validate(self, df_train, df_test, df_test_perturb, classifier_metadata_dict):
        hyperparams = dict()
        try:
            hyperparams = classifier_metadata_dict[self.__TXT_HYPER_FLD]
        except:
            pass

        try:
            df_train.drop(['cycle'], axis=1, inplace=True)
            df_test.drop(['cycle'], axis=1, inplace=True)
            df_test_perturb.drop(['cycle'], axis=1, inplace=True)
        except:
            pass

        dp = DataPreparation()
        df_train_filled = dp.fill_na(df_train)
        [scaler, df_train_norm] = dp.normalize(df_train_filled)

        lc = classifier_metadata_dict[self.__TXT_CLASSIFIER_FLD]
        lc.fit(X = df_train_norm, **hyperparams)
        
        df_test_filled = dp.fill_na(df_test)
        df_test_norm = scaler.transform(df_test_filled)
        preds = lc.predict(df_test_norm)
        preds_proba = lc.predict_proba(df_test_norm)

        df_test_perturb_filled = dp.fill_na(df_test_perturb)
        df_test_perturb_norm = scaler.transform(df_test_perturb_filled)
        preds_perturb = lc.predict(df_test_perturb_norm)
        preds_proba_perturb = lc.predict_proba(df_test_perturb_norm)

        self.__create_result_dict(str(type(lc).__name__), preds, preds_proba, preds_perturb, preds_proba_perturb)
        
        return self.__results
    

def validate(df_train_distance, df_test_distance, df_test_perturb_distance, classifier_metadata_dict):
    adv = AnomalyDetectionValidation()
    results = adv.validate(df_train_distance, df_test_distance, df_test_perturb_distance, 
                            classifier_metadata_dict = classifier_metadata_dict)
    return results