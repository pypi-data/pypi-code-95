import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from upswingutil.resource import get_model_from_cloud_storage, upload_model_to_cloud_storage
from datetime import datetime
from upswingutil.db import Mongodb
from upswingutil.pms import PMS
from loguru import logger


class RevenueForecasting:
    __file_name__ = 'revenue_forecast_{}.pkl'

    def __init__(self, pms: str, orgId: str, propertyId: str):
        self.pms = pms
        self.orgId = orgId
        self.propertyId = propertyId

    def get_data(self, start_date: str, end_date: str) -> list:
        __pipeline__ = list()
        if self.pms == PMS.RMS:
            __pipeline__ = [
                {
                    '$match': {
                        'clientId': int(self.propertyId),
                        'arrivalDate': {
                            '$gte': start_date,
                            '$lte': end_date
                        }
                    }
                }, {
                    '$unwind': {
                        'path': '$daily_revenue'
                    }
                }, {
                    '$match': {
                        'daily_revenue.theDate': {
                            '$gte': '2021-01-01',
                            '$lte': '2021-12-31'
                        }
                    }
                }, {
                    '$project': {
                        'date': {
                            '$dateFromString': {
                                'dateString': '$daily_revenue.theDate'
                            }
                        },
                        'total': {
                            '$add': [
                                '$daily_revenue.accommodation', '$daily_revenue.other'
                            ]
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$date',
                        'total': {
                            '$sum': '$total'
                        }
                    }
                }, {
                    '$sort': {
                        '_id': 1
                    }
                }
            ]
        elif self.pms == PMS.ORACLE:
            __pipeline__ = [
                {
                    '$match': {
                        'hotelId': self.propertyId,
                        'arrivalDate': {
                            '$gte': start_date,
                            '$lte': end_date
                        }
                    }
                }, {
                    '$unwind': {
                        'path': '$daily_activity'
                    }
                }, {
                    '$match': {
                        'daily_activity.date': {
                            '$gte': start_date,
                            '$lte': end_date
                        }
                    }
                }, {
                    '$project': {
                        'date': {
                            '$dateFromString': {
                                'dateString': '$daily_activity.date'
                            }
                        },
                        'total': '$daily_activity.total.amountBeforeTax'
                    }
                }, {
                    '$group': {
                        '_id': '$date',
                        'total': {
                            '$sum': '$total'
                        }
                    }
                }, {
                    '$sort': {
                        '_id': 1
                    }
                }
            ]
        mongo = Mongodb(self.orgId)
        result = mongo.execute_pipeline(mongo.RESERVATION_COLLECTION, __pipeline__)
        mongo.close_connection()
        return result

    def train(self):
        logger.info(f'Training revenue forecasting for property {self.propertyId}')
        file_name = RevenueForecasting.__file_name__.format(self.propertyId)
        start_date = pd.Timestamp("2018-01-01")
        end_date = pd.Timestamp(datetime.now().strftime('%Y-%m-%d'))
        # end date is required to removed future bookings value
        df = pd.DataFrame(self.get_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        if df.shape[0] == 0:
            print(f"Property:: {self.propertyId} Doesn't Have any Data")
            return
        df["_id"] = pd.DatetimeIndex(df["_id"])
        df = pd.DataFrame(pd.date_range(start_date, end_date), columns=["_id"]).merge(df, on=["_id"],
                                                                                      how="outer").fillna(0)
        smooth_model = SimpleExpSmoothing(np.asarray(df.total), initialization_method='heuristic')
        smooth_model_fitted = smooth_model.fit(smoothing_level=0.3)
        yhat = smooth_model_fitted.fittedvalues[:]

        arima_model = ARIMA(yhat, order=(1, 0, 1))
        fitted_model = arima_model.fit()
        upload_model_to_cloud_storage(fitted_model, self.orgId, file_name)
        logger.info(f"New Model created, File saved: {file_name}")
        logger.info(f"Completed Revenue forecasting model for {self.propertyId}")

    def predict(self, start_date, end_date):
        file_name = RevenueForecasting.__file_name__.format(self.propertyId)
        fitted_model = get_model_from_cloud_storage(self.orgId, file_name)


        start_ = pd.Timestamp("2018-01-01")
        p_start = pd.Timestamp(start_date)
        pred_time = pd.date_range(start_date, end_date, normalize=True)
        start_index = (p_start - start_).days
        end_index = start_index + pred_time.shape[0]
        pred_values = fitted_model.get_prediction(start=start_index, end=end_index).predicted_mean

        return pred_time, pred_values[1:]
