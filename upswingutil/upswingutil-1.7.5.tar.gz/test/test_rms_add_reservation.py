import unittest
import firebase_admin
from firebase_admin import credentials

import upswingutil as ul
from upswingutil.pms.rms import ReservationSync
from upswingutil.resource import access_secret_version, setup_logging
import json


class TestRMSReservationV2API(unittest.TestCase):
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
    ul.ENCRYPTION_SECRET = "S1335HwpKYqEk9CM0I2hFX3oXa5T2oU86OXgMSW4s6U="
    ul.MONGO_URI = access_secret_version(ul.G_CLOUD_PROJECT, 'MONGOURI', '1')

    def test_adding_new_reservation(self):
        setup_logging()
        print('Initializing default firebase app')
        cred = json.loads(
            access_secret_version(ul.G_CLOUD_PROJECT, 'Firebase-Aura', '1'))
        cred = credentials.Certificate(cred)
        firebase_admin.initialize_app(cred)

        print('Initializing alvie firebase app')
        cred = json.loads(
            access_secret_version(ul.G_CLOUD_PROJECT, 'Firebase-Alvie', '1'))
        cred = credentials.Certificate(cred)
        firebase_admin.initialize_app(cred, name='alvie')

        resv = ReservationSync('11249')
        resv_list = [1, 28432]
        for _resv_id in resv_list:
            print(f'processing reservation : {_resv_id}')
            resv.process(_resv_id)
            print(f'processed reservation : {_resv_id}')
