# from datetime import timedelta
# from upswingutil.db import Mongodb
# from upswingutil.resource import get_model_from_cloud_storage
# import pandas as pd
#
#
# __file_path__ = 'app/resource/ml/models/revenue_forecast'
# __df_pickle_file__ = 'app/resource/ml/revenue_forecast_df_{}.pkl'
# months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#
# class RevenueForecast:
#
#     def __init__(self, propId, orgId):
#         self.propId = int(propId)
#         self.orgId = str(orgId)
#         self.db = None
#
#     def forecast(self, start, end):
#         self.db = Mongodb(self.orgId)
#         fitted_model = get_model_from_cloud_storage('revenue_forecast', f'revenue_forecast_{self.propId}.pkl')
#         df = get_model_from_cloud_storage('revenue_forecast', f'revenue_forecast_df_{self.propId}.pkl')
#
#         actual_time = df.loc[start:].index
#         today = pd.to_datetime('today')
#         end_2 = pd.date_range(today, end, normalize=True)
#         pred_time = actual_time.append(end_2[1:])
#         df2 = df.reset_index()
#         start_index = df2[df2["_id"] == start].index.values[0]
#         end_index = start_index + pred_time.shape[0]
#         pred_values = fitted_model.get_prediction(start=start_index, end=end_index).predicted_mean
#
#         forecast_array = list()
#         for date, forecast in zip(pred_time, pred_values[1:]):
#             if date < end:
#                 pred = {
#                     "x": str(date.day) + " " + date.month_name()[:3] + " " + str(date.year),
#                     "y": forecast
#                 }
#                 forecast_array.append(pred)
#
#         return forecast_array
#
#     def __del__(self):
#         if self.db:
#             self.db.close_connection()
#
#
# def transform_date(date):
#     return f'{date.day} {months[date.month]} {date.year}'
#
#
# def revenue_forecast_for_property_by_steps(clientId, time_steps):
#     fitted_model = get_model_from_cloud_storage('revenue_forecast', f'revenue_forecast_{clientId}.pkl')
#     forecast_array = fitted_model.forecast(int(time_steps))
#     return list(forecast_array)
#
#
# def revenue_predict_for_property_by_range(clientId, from_date, to_date):
#     days = (to_date - from_date).days
#     result = list()
#     _arr = revenue_forecast_for_property_by_steps(clientId, days)
#     print(days)
#     print(len(_arr))
#     for i in range(days):
#         date = from_date + timedelta(days=i)
#         result.append({
#             "x": str(date.strftime('%d %b %Y')),
#             "y": _arr[i]
#         })
#
#     return result
