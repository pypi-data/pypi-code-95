# import pickle
# from util.db import Firestore, Mongodb
# from util.error_handling import log_error
# import pandas as pd
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler
#
# __file_path__ = './ml/trained_models/booking_categorization'
#
#
# def train_k_means(clientId, df):
#     scaler = StandardScaler()
#     data_scaled = scaler.fit_transform(df)
#
#     SSE = []
#     for cluster in range(1, 20):
#         kmeans = KMeans(n_jobs=-1, n_clusters=cluster, init='k-means++')
#         kmeans.fit(data_scaled)
#         SSE.append(kmeans.inertia_)
#
#     kmeans = KMeans(n_jobs=-1, n_clusters=4, init='k-means++')
#     kmeansfit = kmeans.fit(data_scaled)
#
#     pickle.dump(kmeansfit, open(f'{__file_path__}_{clientId}.pkl', 'wb'))
#
#
# def transform_data(raw_data):
#     # raw_data1=raw_data[raw_data['status']=='Departed']
#     raw_data["departureDate"] = pd.to_datetime(raw_data["departureDate"])
#     raw_data["departureDate"]
#     raw_data["departureDate"].dt.date
#     raw_data["arrivalDate"] = pd.to_datetime(raw_data["arrivalDate"])
#     raw_data["arrivalDate"]
#     raw_data["arrivalDate"].dt.date
#     stay_d = (raw_data['departureDate'] - raw_data['arrivalDate']).dt.days
#     raw_data['stay_d'] = [int(i) for i in stay_d]
#     raw_data['total_rate'] = [float(i) for i in raw_data['totalRate']]
#     df = raw_data[
#         ['booking_type', 'children', 'duration_type', 'total_rate', 'guestId', 'stay_d', 'propertyId', 'categoryId']]
#
#     df = df[df['stay_d'] > 0]
#     df['average_perday'] = df['total_rate'] / df['stay_d']
#     df['guestId'] = [int(i) for i in df['guestId']]
#
#     df = df[df['stay_d'] < 35]
#     df = df[df['total_rate'] < 40000]
#
#     df_dummies = pd.get_dummies(df['booking_type'])
#     df_new = pd.concat([df, df_dummies], axis=1)
#     del df_new['booking_type']
#     df_new.head()
#
#     df = pd.get_dummies(df_new['categoryId'])
#     del df[df.columns[-1]]
#     df = pd.concat([df_new, df], axis=1)
#     del df['categoryId']
#     df.head()
#
#     df = df[["stay_d", "total_rate", 'Urgent Booking']]
#
#     return df
#
#
# def train_booking_categorization_model_by_org(app, clientId):
#     db = Firestore()
#     path = f'{db.org_collection}/{clientId}/{db.sub_collection_properties}'
#     props = db.get_collection(path).stream()
#     for prop in props:
#         train_booking_categorization_model(app, clientId, prop.id)
#
#
# def train_booking_categorization_model(app, dbName, clientId):
#     with app.app_context():
#         db = None
#         result = None
#         try:
#             app.logger.info(
#                 f'Starting training booking categorization model for property {clientId} and client {dbName}')
#             db = Mongodb(dbName)
#             __data_pipeline__ = [
#                 {
#                     '$match': {
#                         "clientId": int(clientId),
#                         'status': 'Departed'
#                     }
#                 },
#                 {
#                     '$project': {
#                         'status': 1, 'departureDate': 1, 'arrivalDate': 1,
#                         'totalRate': '$financial_info_actual.totalRate',
#                         'booking_type': 1, 'children': 1, 'duration_type': 1, 'guestId': 1, 'categoryId': 1,
#                         'propertyId': 1
#                     }
#                 }
#             ]
#             raw_data = pd.DataFrame(list(db.get_collection(db.reservation_collection).aggregate(__data_pipeline__)))
#             if not raw_data.empty:
#                 df = transform_data(raw_data)
#                 train_k_means(clientId, df)
#                 app.logger.info(f"New Model created, File saved: {__file_path__}_{clientId}.pkl")
#                 result = 'success'
#                 app.logger.info(f'Completed training booking categorization model for {clientId}')
#             else:
#                 app.logger.info(f'No sufficient data to train booking categorization model for {clientId}')
#
#         except Exception as e:
#             app.logger.error(e)
#             result = 'failed'
#             log_error(e, f'Failed to train booking categorization model for {clientId}')
#         finally:
#             if db:
#                 db.close_connection()
#             return result
#
#
# class BookingType:
#
#     @classmethod
#     def predict(cls, clientId, stay, spend, booking_type):
#         result = None
#         try:
#             booking_type = 1 if booking_type == 'Urgent Booking' else 0
#             model = pickle.load(open(f'{__file_path__}_{clientId}.pkl', 'rb'))
#             prediction = model.predict([[stay, spend, booking_type]])
#             result = prediction[0] if len(prediction) > 0 else None
#         except Exception as e:
#             log_error(e, f'Failed predicting booking type for {clientId}')
#         finally:
#             return result
#
#
# if __name__ == '__main__':
#     val = BookingType.predict(11290, '27', '30000', 'Pre planned')
#     print(val)
