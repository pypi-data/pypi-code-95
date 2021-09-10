import ftplib
import os
import time
import sys


class FtpUploader:
	"""
	Allows to upload to a FTP account
	"""
	
	def __init__(self, host, username, passwordFile, port=21, logging=None):
		if logging:
			self.logging = logging
		#Retrieve password
		with open(passwordFile) as fp:
			password = fp.readline().strip()

		#Enstablish connection
		self.connection = ftplib.FTP_TLS()
		self.connection.connect(host, port)
		if self.logging:
			self.logging.info("FtpUploader - uploadFile - Connected to ["+host+"]")
		self.connection.login(username, password)
		if self.logging:
			self.logging.info("FtpUploader - uploadFile - Logged as ["+username+"]")
		self.connection.prot_p()
		if self.logging:
			self.logging.info("FtpUploader - uploadFile - Connection secured")

		self.writtenSize = 0
		self.maxSpeed = 0
		self.uploadStart = None

	def addLogging(self, logging):
		"""
		Assign a logging handler
		"""
		self.logging = logging
		if logging:
			self.logging.info("FtpUploader - Assigned logging handler")
		else:
			print("No logging handler given")

	def uploadFile(self, file_path, block_size=262144, max_speed=0):
		"""
		Upload a file - Return the upload status
		block_size	The size of the block to send - Default 256 KiB
		maxSpeed	Speed in KB/s to maintain during transfer - Default 0 -> No limit
		"""
		self.maxSpeed = max_speed * 1024
		if not self.maxSpeed:
			print("Transferring at maximum speed")
		self.uploadStart = time.time()
		name = os.path.basename(file_path).encode("utf-8", "ignore").decode("latin-1", "ignore")
		with open(file_path, 'rb') as fp:
			try:
				self.connection.storbinary('STOR ' + name, fp, block_size, self.throttler)
				if self.logging:
					self.logging.info("FtpUploader - uploadFile - Uploaded [" + name + "] - [" + file_path + "]")
					print("FtpUploader - uploadFile - Uploaded [" + name + "] - [" + file_path + "]")
				return True
			except ftplib.error_perm:
				self.logging.warn("FtpUploader - uploadFile - Permanent error during upload [" + name + "] - [" + file_path + "]")
			except ftplib.error_temp:
				self.logging.warn("FtpUploader - uploadFile - Temporary error during upload [" + name + "] - [" + file_path + "]")
		return False
	
	total_length = 0
	start_time = time.time()

	#This function slow down the transmission during
	def throttler(self, buf):
		i = 0
		sleepTime = 0.1
		sleepSeconds = 5
		#Do nothing if no limit set to max speed
		if not self.maxSpeed:
			return
		#Get the written bytes
		self.writtenSize += sys.getsizeof(buf)
		cycles = sleepSeconds/sleepTime
		while self.writtenSize / (time.time() - self.uploadStart) > self.maxSpeed:
			time.sleep(sleepTime)
			i += 1
			if not i % cycles:
				print("Elapsed: "+str(time.time() - self.uploadStart)+"s, started at "+str(self.uploadStart)+" and written "+str(self.writtenSize/1024/1024)+" MB Sleeping since "+str(sleepSeconds)+" seconds")
				self.logging.info("Elapsed: "+str(time.time() - self.uploadStart)+"s, started at "+str(self.uploadStart)+" and written "+str(self.writtenSize/1024/1024)+" MB Sleeping since "+str(sleepSeconds)+" seconds")
	
	#Tries to gracefully exit
	def __del__(self):
		self.connection.quit()
		self.logging.info("FtpUploader - __del__ - Quit gracefully")
