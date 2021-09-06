# import pickle
# from datetime import datetime
# from flask import current_app
# import pandas as pd
# import calendar
#
#
# class RevenueTrend:
#     model = None
#     months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#     def __init__(self, clientId):
#         self.clientId = clientId
#
#     @classmethod
#     def predict(cls, clientId: int, from_date: datetime, to_date: datetime):
#         current_app.logger.debug(f'Model in use: ml/trained_models/revenue_forecast_property_{clientId}.pkl')
#         cls.model = pickle.load(open(f'ml/trained_models/revenue_forecast_property_{clientId}.pkl', 'rb'))
#         start_date = pd.to_datetime(str(from_date.date().replace(day=calendar.monthrange(from_date.year, from_date.month)[1])))
#         end_date = pd.to_datetime(str(to_date.date().replace(day=calendar.monthrange(to_date.year, to_date.month)[1])))
#         pred_uc = cls.model.get_prediction(start=start_date, end=end_date, dynamic=True)
#         predicted_values = pred_uc.predicted_mean
#
#         return [{'x': cls.months[item.month] + ' - ' + str(item.year), 'y': predicted_values[item]} for item in
#                 predicted_values.keys()]
#
#     @classmethod
#     def forecast(cls, clientId, steps):
#         current_app.logger.debug(f'Model in use: ml/trained_models/revenue_forecast_property_{clientId}.pkl')
#         cls.model = pickle.load(open(f'ml/trained_models/revenue_forecast_property_{clientId}.pkl', 'rb'))
#         pred_uc = cls.model.get_forecast(steps=steps)
#         predicted_values = pred_uc.predicted_mean
#
#         return [{'x': cls.months[item.month] + ' - ' + str(item.year), 'y': predicted_values[item]} for item in
#                 predicted_values.keys()]
#
#     @classmethod
#     def predict_mtd(cls, clientId, steps):
#         current_app.logger.debug(f'Model in use: ml/trained_models/revenue_forecast_{clientId}.pkl')
#         cls.model = pickle.load(open(f'ml/trained_models/revenue_forecast_{clientId}.pkl', 'rb'))
#         date = datetime.now()
#         start_date = pd.to_datetime(f'{date.year}-{date.month}-{calendar.monthrange(date.year, date.month)[1]}')
#         pred_uc = cls.model.get_prediction(start=start_date, end=start_date, dynamic=True)
#         predicted_values = pred_uc.predicted_mean
#
#         return [{'name': cls.months[item.month] + ' - ' + str(item.year), 'value': predicted_values[item]} for item in
#                 predicted_values.keys()]
#
#
# if __name__ == '__main__':
#     val = RevenueTrend.predict(4, 3)
#     print(val)
