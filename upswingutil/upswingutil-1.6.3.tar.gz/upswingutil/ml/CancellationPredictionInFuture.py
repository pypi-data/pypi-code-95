import pandas as pd
import numpy as np
from sklearn import preprocessing
from imblearn.over_sampling import SMOTE
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from upswingutil.db import Mongodb
from upswingutil.pms import PMS
from loguru import logger


class CancellationPredictionInFuture:
    __file_name__ = 'cancellation_prediction_in_future{}.pkl'

    def __init__(self, pms: str, orgId: str ):
        self.pms = pms
        self.orgId = orgId

    def get_data(self) -> list:
        mongo = Mongodb(self.orgId)
        __pipeline__ = list()
        if self.pms == PMS.RMS:
            __pipeline__ = [
                {
                '$addFields': {
                    'cancellation_lead_in': {
                        '$floor': {
                            '$divide': [
                                {
                                    '$subtract': [
                                        {
                                            '$toDate': '$arrivalDate'
                                        }, {
                                            '$toDate': '$cancelledDate'
                                        }
                                    ]
                                }, 60 * 60 * 24 * 1000
                            ]
                        }
                    }
                }
            }, {
                '$addFields': {
                    'durationOfStay': {
                        '$floor': {
                            '$divide': [
                                {
                                    '$subtract': [
                                        {
                                            '$toDate': '$departureDate'
                                        }, {
                                            '$toDate': '$arrivalDate'
                                        }
                                    ]
                                }, 60 * 60 * 24 * 1000
                            ]
                        }
                    }
                }
            }, {
                '$addFields': {
                    'bookingWindowDays': {
                        '$floor': {
                            '$divide': [
                                {
                                    '$subtract': [
                                        {
                                            '$toDate': '$arrivalDate'
                                        }, {
                                            '$toDate': '$createdDate'
                                        }
                                    ]
                                }, 60 * 60 * 24 * 1000
                            ]
                        }
                    }
                }
            }, {
                '$match': {
                    'guests': {
                        '$type': 4
                    }
                }
            }, {
                '$addFields': {
                    'didVisit': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$eq': [
                                            '$status', 'Cancelled'
                                        ]
                                    }, {
                                        '$eq': [
                                            '$status', 'NoShow'
                                        ]
                                    }
                                ]
                            }, 0, 1
                        ]
                    },
                    'geustCount': {
                        '$size': '$guests'
                    }
                }
            }, {
                '$project': {
                    '_id': 1,
                    'cancellation_lead_in': 1,
                    'durationOfStay': 1,
                    'bookingWindowDays': 1,
                    'didVisit': 1,
                    'geustCount': 1,
                    'clientId': 1,
                    'Class': 1
                }
            }
            ]
        
        result = mongo.execute_pipeline(mongo.RESERVATION_COLLECTION, __pipeline__)
        return result

    def train(self):
        logger.info(f'Training revenue forecasting for property {self}')
        file_name = CancellationPredictionInFuture.__file_name__.format(self)
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
        logger.info(f"Completed Revenue forecasting model for {self}")
