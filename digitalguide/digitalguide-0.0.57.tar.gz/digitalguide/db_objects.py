import mongoengine
from telegram.constants import MAX_MESSAGE_LENGTH
import datetime

user_dbname = "reiherbot_user"
class User(mongoengine.Document):
    user_id = mongoengine.StringField(required=True)
    first_name = mongoengine.StringField(required=True, max_length=50)
    last_name = mongoengine.StringField(max_length=50)
    username = mongoengine.StringField(max_length=50)
    language_code = mongoengine.StringField(max_length=10)
    entry_time = mongoengine.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'db_alias': user_dbname}

interaction_dbname = "reiherbot_interaction"
class Interaction(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    state=mongoengine.StringField(max_length=50),
    update_id = mongoengine.IntField()
    first_name = mongoengine.StringField(max_length=50)
    last_name = mongoengine.StringField(max_length=50)
    username = mongoengine.StringField(max_length=50)
    interaction_full = mongoengine.DictField()
    interaction_text = mongoengine.StringField(max_length=MAX_MESSAGE_LENGTH)
    interaction_data = mongoengine.StringField(max_length=MAX_MESSAGE_LENGTH)
    interaction_id = mongoengine.IntField()
    date = mongoengine.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'db_alias': interaction_dbname}

