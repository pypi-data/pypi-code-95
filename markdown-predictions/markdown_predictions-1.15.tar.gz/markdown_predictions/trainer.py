import dill # to enable lambda pickle functionality
import joblib
import numpy as np
import os
import pandas as pd

from prince import MCA
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.experimental import enable_hist_gradient_boosting # to enable HistGradientBoost
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, RobustScaler

from markdown_predictions.clean_data import PreProcessor, outlier_scan
from markdown_predictions.parse_data import LoadSalesData
from markdown_predictions.utils import compute_rmse, linearize_dates

NUMERICS = ['price_PRE',
            'weekly_rank_PRE',
            'quantity_sold_PRE',
            'quantity_sold_sub1_PRE',
            'quantity_sold_sub2_PRE',
            'quantity_sold_sub3_PRE',
            'discount_rate_PRE',
            'discount_rate_sub1_PRE',
            'store_stock_PRE',
            'stock_transit_PRE',
            'total_store_stock_PRE',
            'weekly_cover_PRE',
            'cum_discount_rate_PRE',
            'cum_quantity_sold_PRE',
            'num_sizes_PRE',
            'num_stores_PRE',
            'rate_of_sale_PRE',
            'cum_sellthrough_PRE',
            'zero_stock_PRE',
            'avail_warehouse_stock_PRE',
            'markdown_PRE']

OBJECTS = ['seasonality_PRE',
           'gender_PRE',
           'product_category_PRE',
           'macro_category_PRE',
           'sub_target_PRE']

DATES = ['first_week_sale_PRE']


def get_data(data_path: str) -> pd.DataFrame:
    """ Load in and clean the data """
    load_data = LoadSalesData.load_in_files(data_path)
    pre_processor = PreProcessor(df=load_data.sales_data)
    pre_processor.clean_up_data()

    return pre_processor.df.reset_index(drop=True)


def get_test_data(data_path: str) -> pd.DataFrame:
    """ Load in test data """
    load_data = LoadSalesData.load_in_test_file(data_path)
    pre_processor = PreProcessor(df=load_data.sales_data)
    pre_processor.clean_up_data(train_set=False)
    return pre_processor.df


class Trainer(object):
    """ Class to train the markdown sales prediction model """
    def __init__(self, X, y, remove_outliers=False, threshold=0.1):
        """
            X: pandas DataFrame
            y: pandas Series
        """

        self.pipeline = None
        self.X = X.reset_index(drop=True)
        self.y = y.reset_index(drop=True)
        self.X_nums = NUMERICS
        self.X_objs = OBJECTS
        self.X_dates = DATES
        
        if "image_url" in X.columns:
            self.X.drop(columns=["image_url"], axis=1)

        if remove_outliers:
            for outlier in outlier_scan(self.X, self.X_nums, threshold=threshold):
                self.X = self.X.drop(outlier)
                self.y = self.y.drop(outlier)

    def set_pipeline(self):
        """ Defines the pipeline as a class attribute """
        numeric_pipe = Pipeline([
            ('robustscaler', RobustScaler())
        ])

        object_pipe = Pipeline([
          ("one_hot", OneHotEncoder(sparse=False, handle_unknown="ignore")),
          ("mca", MCA(n_components=2))
        ])

        date_pipe = Pipeline([
          ("linearize", FunctionTransformer(lambda array: linearize_dates(array))),
          ("robustscaler", RobustScaler())
        ])

        preproc_pipe = ColumnTransformer([
            ('numeric', numeric_pipe, self.X_nums),
            ('object', object_pipe, self.X_objs),
            ('datetime', date_pipe, self.X_dates)
        ], remainder="drop")

        self.pipeline = Pipeline([
            ('preproc', preproc_pipe),
            ('regression_model', HistGradientBoostingRegressor(l2_regularization=1.4, learning_rate=0.09, loss='poisson', max_iter=300))
        ])

    def run(self):
        """ Instantiate ML pipeline and fit model """
        self.set_pipeline()
        self.pipeline.fit(self.X, self.y)

    def evaluate(self, X_test, y_test):
        """ Evaluates the pipeline on test data and returns the RMSE """
        y_pred = self.pipeline.predict(X_test)
        rmse = compute_rmse(y_pred, y_test)
        return rmse

    def cross_validated_evaluate(self, cv=5):
        """ Evaluates the pipeline using k-fold cross validation for all of X and y """
        cval = cross_validate(clone(self.pipeline), self.X, self.y, scoring='neg_root_mean_squared_error', cv=cv)
        return cval['test_score'].mean() * -1

    def save_model(self, model, path=""):
        """ Method that saves the model """
        if len(path) > 0:
            path = os.path.join(path, 'markdown_model.joblib')
            joblib.dump(model, path)
        else:
            joblib.dump(model, 'markdown_model.joblib')


def train_and_save_model(
              df: pd.DataFrame,
              model_path: str="",
              remove_outliers: bool=False,
              threshold: float=0.1,
              test_size: float=0.25,
              random_state: int=None):
    """ Train and save model -- markdown_model.joblib """
    y = df["two_week_sales"]
    X = df.drop("two_week_sales", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    # Train and save model locally
    trainer = Trainer(X=X_train, y=y_train, remove_outliers=remove_outliers, threshold=threshold)
    trainer.run()
    rmse = trainer.evaluate(X_test, y_test)
    rmse_baseline = compute_rmse(trainer.y.mean(), y_test)
    rmse_cval = trainer.cross_validated_evaluate()
    trainer.save_model(trainer.pipeline, model_path)
    return {'model_pipeline': trainer.pipeline,
            'test_score': rmse,
            'baseline_score': rmse_baseline,
            'cval_score': rmse_cval}

if __name__ == "__main__":
    # Get and clean data
    df = get_data(os.path.join(os.path.dirname(os.getcwd()),"raw_data"))
    y = df["two_week_sales"]
    X = df.drop("two_week_sales", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    # Train and save model, locally and
    trainer = Trainer(X=X_train, y=y_train, remove_outliers=True)
    trainer.run()
    rmse = trainer.evaluate(X_test, y_test)
    print(f"RMSE Test Score: {rmse}")
    trainer.save_model(trainer.pipeline)
