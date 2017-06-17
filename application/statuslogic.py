import serial
import subprocess
import time
import threading
import datalogic

class Sensor:
	def __init__(self, name, rate):
		self.name = name
		self.rate = rate
		self.thread = None
		self.connection_error = False
		self.serial = self.getSerial()
		self.return_value = None
		self.status = None
		self.thread = None
		self.statusRequestPending = False
		self.waitTime = .1
		self.maximalRequests = 5
		self.startListeningThread()

	def getSerial(self):
		try:
			return serial.Serial(self.name,self.rate)
		except serial.SerialException:
			print("No Serial Device was connected.")
			self.connection_error = True

	def listenToChanges(self):
		# reads status and returns it when finished
		if(not self.connection_error):
			_status = None
			while(1):
				currentValue = self.serial.readline()
				if(currentValue):
					self.statusRequestPending = False
				self.status = currentValue

	def hasConnectionError(self):
		# check if there is a connection error
		return self.connection_error

	def startListeningThread(self):
		if(not self.hasConnectionError()):
			self.thread = threading.Thread(target=self.listenToChanges, args=())
			self.thread.daemon = True
			self.thread.start()

	def requestStatusOnce(self):
		if(not self.hasConnectionError()):
			self.statusRequestPending = True
			self.serial.write('1')

	def makeStatusRequest(self):
		self.statusRequestPending = True
		currentRequest = 1
		while(self.statusRequestPending and currentRequest < self.maximalRequests):
			self.requestStatusOnce()
			currentRequest+=1
			print(currentRequest)
			time.sleep(.1)
		return True

	def returnError(self):
		return {"error": "Device not available"}

	def getCurrentStatus(self):
		if(self.hasConnectionError()):
			self.returnError()
		self.makeStatusRequest()
		return self.status

class DataInterpreter:
	def __init__(self):
		#Todo
		self.databaseConnector = None

	def interpretRawData(self, data):

