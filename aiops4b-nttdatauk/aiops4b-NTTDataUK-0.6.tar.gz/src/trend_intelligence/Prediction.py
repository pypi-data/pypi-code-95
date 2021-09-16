# Imported libraries

import pandas as pd

from greykite.algo.forecast.silverkite.constants.silverkite_holiday import SilverkiteHoliday
from greykite.framework.templates.autogen.forecast_config import ForecastConfig, MetadataParam, ModelComponentsParam, \
    EvaluationPeriodParam
from greykite.framework.templates.forecaster import Forecaster
from greykite.framework.templates.model_templates import ModelTemplateEnum
from greykite.common import constants as cst

from plotly import graph_objs as go

import warnings
warnings.filterwarnings("ignore")

from ml_utils import *



class Prediction:
    def __init__(self,metrics_path,anomaly_start,anomaly_end,country):
        self.metrics_path = metrics_path
        self.anomaly_start = anomaly_start
        self.anomaly_end = anomaly_end
        self.country = country

    def forecast(self,prediction_days):

        # Metrics
        metrics = pd.read_csv(self.metrics_path, index_col=[0])

        # 1. Anomalies
        anomaly_df = pd.DataFrame({
            # start and end date are inclusive
            cst.START_DATE_COL: [self.anomaly_start],
            cst.END_DATE_COL: [self.anomaly_end],
            cst.ADJUSTMENT_DELTA_COL: [np.nan]  # mask as NA
        })

        # Creates anomaly_info dictionary.
        # This will be fed into the template.
        anomaly_info = {
            "value_col": "Value",
            "anomaly_df": anomaly_df,
            "adjustment_delta_col": cst.ADJUSTMENT_DELTA_COL
        }

        # 2. Growth

        growth = {
            "growth_term": "linear"
        }

        # 3. Changepoint detection

        changepoints = {
            "changepoints_dict": dict(
                method="auto",
                yearly_seasonality_order=2,
                regularization_strength=0.6,
                resample_freq="7D",
                potential_changepoint_n=25,
                yearly_seasonality_change_freq="365D",
                no_changepoint_proportion_from_end=0.1
            )
        }

        # 4. Seasonality

        yearly_seasonality_order = 2
        weekly_seasonality_order = 4
        seasonality = {
            "yearly_seasonality": yearly_seasonality_order,
            "quarterly_seasonality": False,
            "monthly_seasonality": False,
            "weekly_seasonality": weekly_seasonality_order,
            "daily_seasonality": False
        }

        # 5. Holidays and events

        events = {
            # These holidays as well as their pre/post dates are modeled as individual events.
            "holidays_to_model_separately": SilverkiteHoliday.ALL_HOLIDAYS_IN_COUNTRIES,
            # all holidays in "holiday_lookup_countries"
            "holiday_lookup_countries": [self.country],  # only look up holidays in Brazil
            "holiday_pre_num_days": 2,  # also mark the 2 days before a holiday as holiday
            "holiday_post_num_days": 2,  # also mark the 2 days after a holiday as holiday
        }

        # Complete model

        metadata = MetadataParam(
            time_col="Time_col",
            value_col="Value",
            freq="D",
            anomaly_info=anomaly_info,
        )

        model_components = ModelComponentsParam(
            seasonality=seasonality,
            growth=growth,
            events=events,
            changepoints=changepoints,
        )

        evaluation_period = EvaluationPeriodParam(
            test_horizon=28,  # 28 days as testing data
            cv_horizon=prediction_days,  # each cv test size is 1 day (same as forecast horizon)
            cv_max_splits=3,  # 3 folds cv
            cv_min_train_periods=300
        )

        # Runs the forecast
        forecaster = Forecaster()

        result = forecaster.run_forecast_config(
            df=metrics,
            config=ForecastConfig(
                model_template=ModelTemplateEnum.SILVERKITE.name,
                forecast_horizon=prediction_days,  # 1 day forecast
                coverage=0.95,  # 95% prediction intervals
                metadata_param=metadata,
                model_components_param=model_components,
                evaluation_period_param=evaluation_period
            )
        )

        forecast = result.forecast
        fig2 = forecast.plot()
        fig2 = go.Figure(fig2)

        forecast_df = forecast.df

        df = pd.DataFrame(forecast_df.iloc[((-prediction_days)-1):-1,2]).reset_index(drop=True)
        df.index += 1

        return df,fig2

#p1 = Prediction('C:\\Users\\julgonza\\PycharmProjects\\test\\metrics_pvalue.csv',"2017-11-23","2017-11-26","Brazil")
#print(p1.forecast(3)[0])
#print(type(p1.forecast(3)))
