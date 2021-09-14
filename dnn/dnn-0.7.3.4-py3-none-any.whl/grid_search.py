from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV
import numpy as np
from . import callbacks
from tensorflow import keras

class Model (keras.Model):
    def predict_classes (self, *args, **kargs):
        y_pred = self.predict(*args, **kargs)
        return np.argmax (y_pred, axis=1)


def make_callbacks (lr):
    list_of_cb = []
    for e in lr or []:
        patience = 0
        if isinstance (e, (tuple, list)):
            try:
                lr, decay_rate, patience = e
            except ValueError:
                lr, decay_rate = e
        else:
            lr, decay_rate = e, 1.0

        if patience:
            list_of_cb.append ([callbacks.LRPlateauDecay (decay_rate, patience)])
        else:
            list_of_cb.append ([callbacks.LREpochDecay (lr, decay_rate)])

    return list_of_cb


def fit (build_fn, xs, ys = None, cv = None, scoring = 'f1_weighted', lr_sched = None, **params):
    if len (ys.shape) > 1:
        ys = np.argmax (ys, axis = 1)

    cbs = make_callbacks (lr_sched)
    if cbs:
        params ['callbacks'] = cbs

    estimator = KerasClassifier (build_fn = build_fn)
    gscv = GridSearchCV (
        estimator = estimator,
        param_grid = params,
        scoring = scoring,
        cv = cv,
        verbose = 10,
        refit = False
    )

    fitted_model = gscv.fit (xs, ys)
    print ('\n_____')
    for i, p in enumerate (fitted_model.cv_results_ ['params']):
        print ('#{:.0f} {:.4f} {}'.format (
            fitted_model.cv_results_ ['rank_test_score'][i],
            fitted_model.cv_results_ ['mean_test_score'][i],
            p)
        )
    print ('Best {:.4f} {}'.format (fitted_model.best_score_, fitted_model.best_params_))
    return fitted_model
