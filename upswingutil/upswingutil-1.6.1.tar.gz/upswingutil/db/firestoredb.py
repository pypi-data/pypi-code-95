from firebase_admin import firestore, get_app


class Firestore:
    org_collection = 'Organizations'
    sub_collection_properties = 'properties'
    credentials = 'credentials'

    def __init__(self, app=None):
        self.firestore_db = firestore.client(app=get_app(app)) if app else firestore.client()

    def get_collection(self, name):
        return self.firestore_db.collection(name)
