# import pandas as pd
# import numpy as np
# from statsmodels.tsa.holtwinters import SimpleExpSmoothing
# from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
# import os
# from util.db import Mongodb
# from datetime import datetime, timedelta
# from util import strfdelta
# from flask import current_app
#
#
# class NumberOfGuestsPerDay:
#     __file_path__ = './ml/trained_models/guest_count_forecasting'
#
#     def __init__(self, app, client=None):
#         self.app = app
#         self.db = None
#         if client:
#             self.client = client
#             self.clientId = self.client["pms"]["clientId"]
#             self.collection = 'Guest Count Forecasting ML'
#             self.start_time = datetime.now()
#             self.api_url = self.client["pms"]["url"]
#             self.status = {
#                 "total_count": 0,
#                 "name": "init",
#                 "count": 0,
#                 "time": str(self.duration()),
#                 "batch": 100,
#                 "interval": 60 * 24 * 6
#             }
#
#     def duration(self):
#         return strfdelta(datetime.now() - self.start_time, "{hours} h : {minutes} min : {seconds} sec")
#
#     def get_data(self, clientId):
#         features = list(self.db.get_collection(self.db.reservation_collection).aggregate(
#             [
#                 {
#                     '$match': {
#                         'status': {
#                             '$nin': [
#                                 'Cancelled'
#                             ]
#                         },
#                         'clientId': clientId
#                     }
#                 }, {
#                 '$unwind': {
#                     'path': '$daily_rates',
#                     'includeArrayIndex': 'daily_rates_index'
#                 }
#             }, {
#                 '$project': {
#                     'date': '$daily_rates.stayDate',
#                     'adults': '$adults',
#                     'children': '$infants'
#                 }
#             }, {
#                 '$group': {
#                     '_id': '$date',
#                     'total_adults': {
#                         '$sum': '$adults'
#                     },
#                     'total_children': {
#                         '$sum': '$children'
#                     }
#                 }
#             }, {
#                 '$sort': {
#                     '_id': 1
#                 }
#             }, {
#                 '$project': {
#                     'total': {
#                         '$add': [
#                             '$total_adults', '$total_children'
#                         ]
#                     }
#                 }
#             }, {
#                 '$addFields': {
#                     '_id': {
#                         '$dateFromString': {
#                             'dateString': '$_id'
#                         }
#                     }
#                 }
#             }
#             ]
#         ))
#         return features
#
#     def sync(self):
#         with self.app.app_context():
#             self.db = Mongodb(self.clientId)
#             current_app.logger.info(f'Starting Sync of Guest Count Forecasting for client {self.clientId}')
#             client_list = self.db.get_collection(self.db.reservation_collection).distinct("clientId")
#             self.status['batch'] = len(client_list)
#             for index, client_name in enumerate(client_list):
#                 file_name = f'{self.__file_path__}_{client_name}.pkl'
#                 self.status['name'] = f"Training model {file_name}"
#                 self.status['count'] = (index + 1)
#                 self.status['time'] = str(self.duration())
#                 current_app.logger.info(f"Training model {file_name}")
#                 df = pd.DataFrame(self.get_data(client_name))
#                 today = pd.to_datetime('today').normalize()
#                 df = df.set_index("_id").loc[:today].reset_index()
#                 df = pd.DataFrame(pd.date_range(pd.Timestamp("2018-01-01"), today), columns=["_id"]).merge(df,
#                                                                                                            on=["_id"],
#                                                                                                            how="outer").fillna(
#                     0)
#
#                 # Smoothing the data to reduce so much Noise in values to get better predictions
#                 smooth_model = SimpleExpSmoothing(np.asarray(df.total), initialization_method='heuristic')
#                 smooth_model_fitted = smooth_model.fit(smoothing_level=0.5)
#                 yhat = smooth_model_fitted.fittedvalues[:]
#                 smooth_value = yhat
#
#                 # Arime model intialize
#                 arima_model = ARIMA(smooth_value, order=(1, 0, 1))
#                 fitted_model = arima_model.fit()
#
#                 # save the model
#                 fitted_model.save(file_name)
#                 print(f"New Model created, File saved: {file_name}")
#             end_time = datetime.now()
#             diff = self.duration()
#             self.status['name'] = f'Completed'
#             self.status['time'] = str(diff)
#             interval = self.status['interval']
#             self.status['name'] = f'Next job run at {self.start_time + timedelta(minutes=interval)}'
#             current_app.logger.info(f"Completed Guest Count forecasting model for {self.clientId}")
#
#     def train_client(self, clientId=None, Trainable=False):
#         file_name = str(clientId) + "_NOG.pkl"
#         file_present = file_name in os.listdir(".")
#         if (Trainable or not file_present):
#             df = pd.DataFrame(self.get_data(clientId))
#             today = pd.to_datetime('today').normalize()
#             df = df.set_index("_id").loc[:today].reset_index()
#             df = pd.DataFrame(pd.date_range(pd.Timestamp("2018-01-01"), today), columns=["_id"]).merge(df, on=["_id"],
#                                                                                                        how="outer").fillna(
#                 0)
#             # plt.bar(df._id, df.total)
#             # plt.savefig(str(clientId)+".png",dpi=150)
#             # Smoothing the data to reduce so much Noise in values to get better predictions
#             smooth_model = SimpleExpSmoothing(np.asarray(df.total), initialization_method='heuristic')
#             smooth_model_fitted = smooth_model.fit(smoothing_level=0.5)
#             yhat = smooth_model_fitted.fittedvalues[:]
#             smooth_value = yhat
#
#             # Arime model intialize
#             arima_model = ARIMA(smooth_value, order=(1, 0, 1))
#             fitted_model = arima_model.fit()
#
#             # save the model
#             fitted_model.save(file_name)
#             print(f"New Model created, File saved: {file_name}")
#
#     def predict(self, clientId, start_date, end_date):
#         file_name = f'{self.__file_path__}_{clientId}.pkl'
#         fitted_model = ARIMAResults.load(file_name)
#
#         start_ = pd.Timestamp("2018-01-01")
#         p_start = pd.Timestamp(start_date)
#         pred_time = pd.date_range(start_date, end_date, normalize=True)
#         start_index = (
#                     p_start - start_).days  ##df[df._id == pd.to_datetime(start)].index.values[0] ## I used dataframe but you have to mention it from your side, Like revenue forecasting
#         end_index = start_index + pred_time.shape[0]
#         pred_values = fitted_model.get_prediction(start=start_index, end=end_index).predicted_mean
#
#         # #     Plotting the chart
#         #     plt.figure(figsize=(10,6), dpi=150)
#         # #     plt.plot(actual_time, actual_values, label="Actual", c='cornflowerblue')
#         #     plt.plot(pred_time, pred_values[1:], label="Predicted", color='darkorange') # try plt.bar instead of plt.plot
#         #     plt.legend(fontsize=15)
#         #     plt.savefig("Forecast", dpi=150)
#         #     plt.close()
#
#         forecast_array = list()
#         for date, forecast in zip(pred_time, pred_values[1:]):
#             pred = {
#                 "x": str(date.day) + " " + date.month_name()[:3] + " " + str(date.year),
#                 "y": forecast
#             }
#             forecast_array.append(pred)
#
#         return forecast_array
#
#     def __del__(self):
#         if self.db:
#             self.db.close_connection()
