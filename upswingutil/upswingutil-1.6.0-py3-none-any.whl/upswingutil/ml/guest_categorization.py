# """
# Recommendation System : Version 1
# """
# from upswingutil.db import Mongodb
# from loguru import logger
# import pandas as pd
#
#
# class CustomerRecommendationCategory:
#
#     def __init__(self, org_id: str):
#         self.mongo = Mongodb(org_id)
#         self.db = self.mongo.get_collection(Mongodb.RESERVATION_COLLECTION)
#         self.result = self.db.aggregate(list(
#             [
#                 {
#                     '$match': {
#                         'status': 'Departed'
#                     }
#                 }, {
#                 '$addFields': {
#                     'durationInDays': {
#                         '$divide': [
#                             {
#                                 '$subtract': [
#                                     {
#                                         '$toDate': '$departureDate'
#                                     }, {
#                                         '$toDate': '$arrivalDate'
#                                     }
#                                 ]
#                             }, 1000 * 60 * 60 * 24
#                         ]
#                     }
#                 }
#             }, {
#                 '$addFields': {
#                     'durationBeforeArrival': {
#                         '$divide': [
#                             {
#                                 '$subtract': [
#                                     {
#                                         '$toDate': '$arrivalDate'
#                                     }, {
#                                         '$toDate': '$createdDate'
#                                     }
#                                 ]
#                             }, 1000 * 60 * 60 * 24
#                         ]
#                     }
#                 }
#             }, {
#                 '$project': {
#                     'adults': 1,
#                     'children': {
#                         '$toBool': '$children'
#                     },
#                     'booking_level': 1,
#                     'booking_type': 1,
#                     'duration_type': 1,
#                     'reservationType': 1,
#                     'durationInDays': {
#                         '$round': [
#                             '$durationInDays', 0
#                         ]
#                     },
#                     'durationBeforeArrival': {
#                         '$round': [
#                             '$durationBeforeArrival', 0
#                         ]
#                     }
#                 }
#             }
#             ]
#         ))
#
#         self.data = pd.DataFrame(self.result)
#         self.data["Class"] = 'None'
#
#         self.db.update_many(
#             {},
#             {'$set': {'Class': "None", 'guest_type': "None"}}
#         )
#
#     def _preprocessing(self):
#         """
#             Preprocesssing Function: \n
#             \t 1. Filtering the Rows with "durationBeforeArrival" < 0\n
#             \t 2. Having atleast 1 Adult in the Reservations\n
#             \t 3. Changing the Number and Name of the categories in 'booking_type' and 'duration_type'
#         """
#         logger.debug('Processing data for Guest Classification')
#         # Preprocessing Steps:
#         # 1. Filtering the Rows with "durationBeforeArrival" < 0
#         self.data = self.data.query('durationBeforeArrival >= 0')
#
#         # 2. Having atleast 1 Adult in the Reservations
#         self.data = self.data.query('adults>0')
#
#         # 3. Changing the Number and Name of the categories in 'booking_type' and 'duration_type'
#         categories = ['last second', 'last minute', 'about 1 week', 'about 2 week', 'about 1 month', 'about 2 months',
#                       'about 3 months', 'about 1 year', 'more than 1 year']
#         dur_type = pd.cut(self.data.durationInDays, bins=[-1, 1, 3, 7, 14, 30, 60, 90, 365, 500], labels=categories)
#         self.data.duration_type = dur_type
#         bef_arr = pd.cut(self.data.durationBeforeArrival, bins=[-1, 1, 3, 7, 14, 30, 60, 90, 365, 500],
#                          labels=categories)
#         self.data.booking_type = bef_arr
#
#     def create_guest_categories(self):
#         """
#             Function to create Guest Categories {'Family', 'Duo', 'Single', 'Busniess', 'Group'} due to their specific reservation's features.
#         """
#         logger.debug('Create guest categories')
#         self.data["guest_type"] = 'GUEST'
#         self.data.update(self.data.query("children == True").replace('GUEST', "Family"))
#         self.data.update(self.data.query("adults == 2").replace('GUEST', "Duo"))
#         self.data.update(self.data.query("adults == 1").replace('GUEST', "Single"))
#         self.data.update(self.data.query("adults > 2 and durationInDays < 8").replace('GUEST', "Busniess"))
#         self.data.update(self.data.query("adults > 2 and durationInDays >= 8").replace('GUEST', "Group"))
#
#     def get_temp_class(self):
#         """
#             Temporary Customer: Customer Classification for respective offers
#         """
#         booking_type_1 = ["last second", "last minute", "about 1 week"]
#         duration_type_1 = ["last second", "last minute"]
#         booking_level_1 = ["gold", "platinum"]
#         booking_type_2 = ["last second"]
#         duration_type_2 = ["about 1 week", "about 2 week"]
#         booking_level_2 = ["gold", "platinum"]
#
#         temp = self.data.query(
#             f'booking_type in {booking_type_1} and duration_type in {duration_type_1} and booking_level not in {booking_level_1} or \
#             (booking_type in {booking_type_2} and duration_type in {duration_type_2} and booking_level not in {booking_level_2} and children == False)').replace(
#             'None', "Temporary")
#
#         self.data.update(temp)
#
#     def get_good_class(self):
#         """
#             Good Customer: Customer Classification for respective offers
#         """
#         booking_type_1 = ["about 1 week", "about 2 week", "last minute"]
#         duration_type_1 = ["about 1 week", "about 2 week"]
#         booking_type_2 = ["about 2 week", "about 1 month", "about 2 months", "about 3 months"]
#         duration_type_2 = ["last minute"]
#         booking_type_3 = ["about 1 month", "about 2 months", "about 3 months", "about 1 year", "more than 1 year"]
#         duration_type_3 = ["about 1 week", "last second", "last minute"]
#         booking_type_4 = ["last second", "last minute"]
#         duration_type_4 = ["about 1 month"]
#         booking_level_1 = ["platinum"]
#         booking_level_2 = ["platinum"]
#         booking_level_3 = ["gold"]
#         booking_level_4 = ["platinum"]
#
#         good = self.data.query(
#             f'(booking_type in {booking_type_1} and duration_type in {duration_type_1} and booking_level not in {booking_level_1}) or\
#             (booking_type in {booking_type_2} and duration_type in {duration_type_2} and booking_level not in {booking_level_2}) or\
#                 (booking_level in {booking_level_3} and duration_type in {duration_type_3} and booking_type not in {booking_type_3}) or\
#                     (booking_type in {booking_type_4} and duration_type in {duration_type_4} and booking_level not in {booking_level_4})').replace(
#             "None", "Good")
#
#         self.data.update(good)
#
#     def get_loyal_class(self):
#         """
#             Loyal Customer: Customer Classification for respective offers
#         """
#         booking_type_1 = ["about 1 week", "about 2 week", "about 1 month"]
#         duration_type_1 = ["about 1 month", "about 2 months"]
#         booking_type_2 = ["about 1 month", "about 2 months", "about 3 months"]
#         duration_type_2 = ["about 1 week", "about 2 week", "about 1 month"]
#         booking_type_3 = ["last second", "last minute"]
#         duration_type_3 = ["about 2 months"]
#         booking_level = ["platinum"]
#
#         loyal = self.data.query(
#             f'booking_level not in {booking_level} and ((booking_type in {booking_type_1} and duration_type in {duration_type_1}) or\
#             (booking_type in {booking_type_2} and duration_type in {duration_type_2}) or\
#                 (booking_type in {booking_type_3} and duration_type in {duration_type_3}))').replace('None', 'Loyal')
#
#         self.data.update(loyal)
#
#     def get_vip_class(self):
#         """
#             VIP Customer: Customer Classification for respective offers
#         """
#         booking_type_1 = ["about 2 months", "about 3 months", "about 1 year", "more than 1 year"]
#         duration_type_1 = ["about 2 months"]
#         duration_type_2 = ["about 3 months", "about 1 year", "more than 1 year"]
#
#         vip = self.data.query(f'booking_level == "platinum" or \
#             (booking_type in {booking_type_1} and duration_type in {duration_type_1}) or\
#                 (duration_type in {duration_type_2})').replace("None", "VIP")
#
#         self.data.update(vip)
#
#     def update_to_database(self):
#         """
#             Function updates the filtered Data and it's calculated Class to the Database (MongoDB in our Case)
#         """
#         for l, v, g in zip(self.data._id, self.data.Class, self.data.guest_type):
#             self.db.update_many(
#                 {'_id': l},
#                 {'$set': {'Class': v, 'guest_type': g}},
#                 upsert=True
#             )
#
#     def process(self):
#         self._preprocessing()
#         self.create_guest_categories()
#         self.get_temp_class()
#         self.get_good_class()
#         self.get_loyal_class()
#         self.get_vip_class()
#         self.update_to_database()
#         logger.debug('Completed Processing Guest Categorization')
#
#     def __del__(self):
#         if self.mongo:
#             self.mongo.close_connection()
#
#
# if __name__ == '__main__':
#     orgId = '11249'
#     d = CustomerRecommendationCategory(orgId)
#     d.process()
