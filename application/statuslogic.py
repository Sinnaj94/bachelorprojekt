import serial
import subprocess
import time
import threading
from datalogic import DatabaseGet

# Sensor: Allows connection to a hardware Sensor
class Sensor:
	# name = name of usb host of sensor
	# rate = baud rate of sensor
	def __init__(self, name, rate):
		self.name = name
		self.rate = rate
		self.thread = None
		self.connection_error = False
		self.serial = self.getSerial()
		self.status = None
		self.thread = None
		self.statusRequestPending = False
		self.waitTime = .1
		self.maximalRequests = 5
		self.startListeningThread()

	# build serial connection to sensor
	def getSerial(self):
		try:
			return serial.Serial(self.name,self.rate)
		except serial.SerialException:
			print("No Serial Device was connected.")
			self.connection_error = True

	# listen to changes of sensor
	def listenToChanges(self):
		# reads status and returns it when finished
		if(not self.connection_error):
			_status = None
			while(1):
				currentValue = self.serial.readline()
				if(currentValue):
					self.statusRequestPending = False
				self.status = currentValue

	# check if there was a connection error at the beginning
	def hasConnectionError(self):
		return self.connection_error

	# starts listening thread to sensor
	def startListeningThread(self):
		if(not self.hasConnectionError()):
			self.thread = threading.Thread(target=self.listenToChanges, args=())
			self.thread.daemon = True
			self.thread.start()

	# requests the status by sending a byte to the hardware sensor
	def requestStatusOnce(self):
		if(not self.hasConnectionError()):
			self.statusRequestPending = True
			self.serial.write('1')

	# make multiple requests until answer is given
	# TODO: implement timeout
	def makeStatusRequest(self):
		self.statusRequestPending = True
		currentRequest = 1
		while(self.statusRequestPending and currentRequest < self.maximalRequests):
			self.requestStatusOnce()
			currentRequest+=1
			print(currentRequest)
			time.sleep(.1)
		return True

	# return an error if could not connect
	def returnError(self):
		return {"error": "Device not available"}

	# make a status request and return value
	def getCurrentStatus(self):
		if(self.hasConnectionError()):
			self.returnError()
		self.makeStatusRequest()
		return self.status

class Status:
	# sensor = sensor object
	# statusId = id of sensor - automatically generated
	def __init__(self, sensor, databaseGet):
		self.sensor = sensor
		self.statusId = generateStatusId()
		self.databaseGet = databaseGet

	# generate status id by looking up the highest value in database and incrementing
	def generateStatusId():
		return databaseGet.getHighestId() + 1


