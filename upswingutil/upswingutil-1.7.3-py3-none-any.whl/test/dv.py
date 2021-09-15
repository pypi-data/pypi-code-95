import upswingutil as ul
from upswingutil.db import MongodbV2
from upswingutil.db.model import PropertyModel, ReservationModel


ul.MONGO_URI = 'mongodb://AdminUpSwingGlobal:Upswing098812Admin0165r@dev.db.upswing.global:27017/?authSource=admin&readPreference=primary&appname=Agent%20Oracle%20Dev&ssl=false'


if __name__ == '__main__':
    print('test-1')
    orgId = 'OHIPB2'
    mongo = MongodbV2(orgId)
    prop = PropertyModel(_id='SAND03')
    prop.name = 'test'
    mongo.save(prop)
    mongo.close_connection()
    print('test-2')
    mongo = MongodbV2(orgId)
    resv = ReservationModel(_id="t2")
    resv.agent = 'test'
    resv.hotel = prop
    mongo.save(resv)
    mongo.close_connection()
