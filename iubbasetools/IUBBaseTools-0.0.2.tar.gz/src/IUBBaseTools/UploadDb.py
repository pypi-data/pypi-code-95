
class UploadDb:
	def __init__(self, path):
		self.path = path

	def saveDataPlain(self, dataset):
		"""
		Store an array into the DB
		:param dataset: List of entry data to store in the DB
		:return: None
		"""
		with open(self.path, 'w') as fd:
			for item in dataset:
				fd.write(item.strip()+"\n")
		fd.close()

	def appendDataPlain(self, line):
		"""
		Append a single line
		:param line: The new record to add to DB
		:return: None
		"""
		fd = open(self.path, 'a')
		fd.write(line+"\n")
		fd.close()

	def restoreDataPlain(self):
		"""
		Restore all the data as an array
		:return: The list of record read from DB
		"""
		fd = open(self.path, 'r')
		content = fd.readlines()
		val = [x.strip() for x in content]
		fd.close()
		return val
