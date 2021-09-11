from pymongo import MongoClient
class userstate():
    def __init__(self,mongodbcollection):
        self.dbcollection = mongodbcollection
    def setuserstate(self,user, userstate):
        try:
            res = self.dbcollection.update_one({"userId": user}, {"$set": userstate}, upsert=True)
        except:
            res = self.dbcollection.insert_one(userstate)
        return res

    def getuserstate(self,userid):
        userstate = self.dbcollection.find_one({"userId": userid})
        if userstate is None:
            userstate = {"userId": userid}
            self.dbcollection.insert_one(userstate)
        return userstate



