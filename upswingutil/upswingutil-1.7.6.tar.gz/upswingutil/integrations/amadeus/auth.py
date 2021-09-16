import urllib
import requests
from datetime import datetime, timedelta
from upswingutil.db import Firestore
from upswingutil.resource import decrypt
from upswingutil.schema import Token
from loguru import logger
from amadeus import Client


def validate_key(expiryDate):
    """
    Validated whether the token is still valid or not
    :param expiryDate:
    :return:
    """
    try:
        if expiryDate is None:
            return False
        return datetime.fromisoformat(expiryDate) > (datetime.now() + timedelta(minutes=5))
    except Exception as e:
        logger.error('Error while validating key')
        logger.error(e)
        return False


def get_key(production: bool = True) -> Client:
    """
    This method generates auth token for provided org_id, in case of refreshing token,
    provide refresh_token, to generate new token using it.

    :return: instance of Token
    """
    try:
        db = Firestore()
        production = 'production' if production else 'test'
        secret = db.get_collection(db.credentials).document('amadeus').get().to_dict()
        amadeus = Client(
            hostname=production,
            client_id=secret.get('clientId'),
            client_secret=secret.get('clientSecret')
        )
        logger.info(f'Amadeus token generated for : {amadeus.hostname} env')
        return amadeus
    except Exception as e:
        logger.error('Error generating token key oracle')
        logger.error(e)


if __name__ == '__main__':
    import upswingutil as ul
    import os
    import json
    import firebase_admin
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
    cred = json.loads(ul.resource.access_secret_version(os.getenv('G_CLOUD_PROJECT', 'aura-staging-31cae'), 'Firebase-Aura', '1'))
    cred = firebase_admin.credentials.Certificate(cred)
    firebase = firebase_admin.initialize_app(cred)
    amadeus = get_key(production=False)
