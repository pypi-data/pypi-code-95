"""
XGBoost wrapper to simplify early stopping

@author: Francesco Baldisserri
@creation date: 8/9/2021
"""

from sklearn.model_selection import train_test_split
from xgboost.sklearn import XGBRegressor, XGBClassifier


class XGBRegressorWrapper(XGBRegressor):
    def fit(self, x, y):
        x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, shuffle=True)
        return super().fit(x_train, y_train, eval_set=[(x_val, y_val)],
                           early_stopping_rounds=int(self.n_estimators/10),
                           verbose=False)


class XGBClassifierWrapper(XGBClassifier):
    def fit(self, x, y):
        x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, shuffle=True)
        return super().fit(x_train, y_train, eval_set=[(x_val, y_val)],
                           early_stopping_rounds=int(self.n_estimators / 10),
                           verbose=False)