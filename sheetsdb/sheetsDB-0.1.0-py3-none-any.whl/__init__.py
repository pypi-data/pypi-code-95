"""
example usage:
from sheetsDB import Db
db = Db('<bot credentials in a json file>',"<YOUR URL>")
with db.var1 as storage:
	do_something_with_storage()
	db.var1.push()# force to push
"""
from .db import Db

def Storage(*a,**k)->Db:
	raise NameError("Replace \"Storage\" with \"Db\" in your files!")