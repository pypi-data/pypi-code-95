import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from upswingutil.db import Mongodb
from datetime import datetime
from upswingutil.db.model import Status
from loguru import logger
from upswingutil.resource import upload_model_to_cloud_storage, get_model_from_cloud_storage
from upswingutil.pms.rms import NAME as RMS
from upswingutil.pms.oracle import NAME as ORACLE


class ReservationCountForecast:
    """
    Predict reservation count for a given date range.
    """
    __file_name__ = 'booking_count_forecast_{}.pkl'

    def __init__(self, pms, orgId, propertyId: str):
        self.pms = pms
        self.orgId = orgId
        self.propertyId = propertyId

    def get_data(self, start_date, end_date):
        mongo = Mongodb(self.orgId)
        __pipeline__ = list()
        if self.pms == RMS:
            __pipeline__ = [
                {
                    '$match': {
                        "clientId": int(self.propertyId),
                        'status': {
                            '$nin': [
                                Status.MAINTENANCE.value
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'Time': '$arrivalDate'
                    }
                }, {
                    '$addFields': {
                        'Time': {
                            '$substr': [
                                '$Time', 0, 10
                            ]
                        }
                    }
                }, {
                    '$addFields': {
                        'Time': {
                            '$dateFromString': {
                                'dateString': '$Time'
                            }
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$Time',
                        'Counts': {
                            '$sum': 1
                        }
                    }
                }, {
                    '$sort': {
                        '_id': 1
                    }
                }, {
                    '$match': {
                        '_id': {
                            '$gte': start_date
                        }
                    }
                }, {
                    '$match': {
                        '_id': {
                            '$lte': end_date
                        }
                    }
                }
            ]
        elif self.pms == ORACLE:
            __pipeline__ = [
                {
                    '$match': {
                        'hotelId': self.propertyId,
                        'status': {
                            '$nin': [
                                Status.MAINTENANCE.value
                            ]
                        },
                        'arrivalDate': {
                            '$gte': start_date,
                            '$lte': end_date
                        }
                    }
                }, {
                    '$project': {
                        'Time': '$arrivalDate'
                    }
                }, {
                    '$addFields': {
                        'Time': {
                            '$substr': [
                                '$Time', 0, 10
                            ]
                        }
                    }
                }, {
                    '$addFields': {
                        'Time': {
                            '$dateFromString': {
                                'dateString': '$Time'
                            }
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$Time',
                        'Counts': {
                            '$sum': 1
                        }
                    }
                }, {
                    '$sort': {
                        '_id': 1
                    }
                }
            ]
        result = mongo.execute_pipeline(mongo.RESERVATION_COLLECTION, __pipeline__)
        mongo.close_connection()
        return result

    def train(self):
        logger.info(f'Training reservation count forecasting for property {self.propertyId}')
        file_name = ReservationCountForecast.__file_name__.format(self.propertyId)
        start_date = pd.Timestamp("2018-01-01")
        end_date = pd.Timestamp(datetime.now().strftime('%Y-%m-%d'))
        df = pd.DataFrame(self.get_data(start_date, end_date))
        if df.shape[0] == 0:
            print(f"Property:: {self.propertyId} Doesn't Have any Data")
            return
        df["_id"] = pd.DatetimeIndex(df["_id"])
        df = pd.DataFrame(pd.date_range(start_date, end_date), columns=["_id"]).merge(df, on=["_id"],
                                                                                      how="outer").fillna(0)
        df.set_index("_id", inplace=True)
        if df.shape[0] > 10:
            smooth_model = SimpleExpSmoothing(np.asarray(df.Counts), initialization_method='heuristic')
            smooth_model_fitted = smooth_model.fit(smoothing_level=0.3)
            yhat = smooth_model_fitted.fittedvalues[:]
        else:
            yhat = df.Counts

        arima_model = ARIMA(yhat, order=(3, 1, 2))
        fitted_model = arima_model.fit()
        upload_model_to_cloud_storage(fitted_model, self.orgId, file_name)
        logger.info(f"New Model created, File saved: {file_name}")
        logger.info(f"Completed Reservation count forecasting model for {self.propertyId}")

    def predict(self, start_date, end_date):
        file_name = ReservationCountForecast.__file_name__.format(self.propertyId)
        fitted_model = get_model_from_cloud_storage(self.orgId, file_name)

        start_ = pd.Timestamp("2018-01-01")
        p_start = pd.Timestamp(start_date)
        pred_time = pd.date_range(start_date, end_date, normalize=True)
        start_index = (p_start - start_).days  # df[df._id == pd.to_datetime(start)].index.values[0] ## I used dataframe but you have to mention it from your side, Like revenue forecasting
        end_index = start_index + pred_time.shape[0]
        pred_values = fitted_model.get_prediction(start=start_index, end=end_index).predicted_mean

        return pred_time, pred_values[1:]
