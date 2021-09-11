import threading, queue
from multiprocessing import Process, Queue
import datetime

from pymongo import MongoClient
import copy


def create_connection_to_mongo(db_name, collection_name, url):
	client = MongoClient(url)
	local_func = locals()
	exec(f"connected = client.{db_name}.{collection_name}", globals(), local_func)
	connected = local_func["connected"]
	return connected


class MongoBaseModel:
	def __init__(self, **kwargs):
		# user must defind self.db_name, self.collection_name, self.url, self.fields
		# default self.create_thread = Process

		self.collection = create_connection_to_mongo(self.db_name, self.collection_name, self.url)

		self.data = copy.deepcopy(kwargs)
		self.create_thread = Process

		self.validate_data()

	def create_in_thread(self, data):
		create_connection_to_mongo(self.db_name, self.collection_name, self.url).insert_one(data)

	def create(self, take_result=False):
		self.data['create_at'] = datetime.datetime.now()

		if take_result:
			return self.collection.insert_one(self.data)
		else:
			self.create_thread(target=self.create_in_thread, args=(self.data,)).start()

	def validate_data(self):
		for field in self.data:
			if field not in self.fields:
				del self.data[field]



