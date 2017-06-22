import serial
import subprocess
import time
import threading
from datalogic import DataConnector

# Sensor: Allows connection to a hardware Sensor
class Sensor:
	# name = name of usb host of sensor
	# rate = baud rate of sensor
	def __init__(self, name, rate, sensorId):
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
		self.id = sensorId
		self.startListeningThread()

	def disconnect(self):
		self.connection_error = True
		self.serial.close()
	# build serial connection to sensor
	def getSerial(self):
		try:
			return serial.Serial(self.name,self.rate)
		except serial.SerialException:
			print("Serial Device on port "+ self.name+ " could not be connected.")
			self.connection_error = True

	# listen to changes of sensor
	def listenToChanges(self):
		# reads status and returns it when finished
		_status = None
		while(not self.connection_error):
			try:
				currentValue = self.serial.readline().splitlines()[0]
				if(currentValue):
					self.statusRequestPending = False
					self.status = currentValue
			except(serial.SerialException):
				currentValue = "Not available"
			

	# check if there was a connection error at the beginning
	def hasConnectionError(self):
		return self.connection_error

	# starts listening thread to sensor
	def startListeningThread(self):
		self.thread = threading.Thread(target=self.listenToChanges, args=())
		self.thread.daemon = True
		self.thread.start()

	# requests the status by sending a byte to the hardware sensor
	def requestStatusOnce(self, requestDigit):
		if(not self.hasConnectionError()):
			self.statusRequestPending = True
			self.serial.write(str(requestDigit))

	# make multiple requests until answer is given
	# TODO: implement timeout
	def makeStatusRequest(self, requestDigit):
		self.statusRequestPending = True
		currentRequest = 0
		while(self.statusRequestPending and currentRequest < self.maximalRequests):
			self.requestStatusOnce(requestDigit)
			currentRequest+=1
			time.sleep(.1)
		if(self.statusRequestPending):
			return False
		return self.status

	# make a status request and return value
	def getCurrentStatus(self, requestDigit):
		if(self.hasConnectionError()):
			return False
		return self.makeStatusRequest(requestDigit)

	def getId(self):
		return self.id

	def toDict(self):
		return {'id': self.id, 'name': self.name, 'rate': self.rate}


class Status:
	# sensor = sensor object
	# statusId = id of sensor - automatically generated
	def __init__(self, databaseGet, statusId, sensor, name, dataType, requestDigit, unit=None, prefix=None, postfix=None):
		#self.sensor = sensor
		self.databaseGet = databaseGet
		if(not statusId):
			self.statusId = self.generateStatusId()
		else:
			self.statusId = statusId
		self.sensor = sensor
		self.name = name
		self.prefix = prefix
		self.postfix = postfix
		self.dataType = dataType
		self.unit = unit
		self.requestDigit = requestDigit

	def getSensor(self):
		return self.sensor

	# return status configuration as dict object
	def toDict(self):
		return {'unit': self.unit, 'sensor': self.sensor.getId(), 'name': self.name, 'prefix': self.prefix, 'postfix': self.postfix, 'requestDigit': self.requestDigit, 'dataType': self.dataType}

	# generate status id by looking up the highest value in database and incrementing
	def generateStatusId(self):
		return self.databaseGet.getHighestId() + 1

	# request sensor and format the status
	def getFormattedStatus(self, requestSensor = True):
		sensorStatus = None
		if(requestSensor):
			sensorStatus = self.sensor.getCurrentStatus(self.requestDigit)
		return {'value': sensorStatus, 'name': self.name ,'prefix': self.prefix, 'postfix': self.postfix, 'id': self.statusId, 'dataType': self.dataType, 'unit': self.unit}

	def getStatusId(self):
		return self.statusId

	def getStatusName(self):
		return self.name

# generate status with including data from database
class StatusFactory:
	def __init__(self, databaseGet, sensorList):
		self.databaseGet = databaseGet
		self._sensorList = sensorList
		self._statusList = self.produceStatusFromDatabase()

	def produceStatusFromDatabase(self):
		status = self.databaseGet.getStatus()
		statusList = []
		for currentStatus in status:
			sensorObject = None
			for sensor in self._sensorList:
				if(sensor.getId() == currentStatus['sensor']):
					sensorObject = sensor
			statusObject = Status(self.databaseGet, currentStatus['id'], sensorObject, currentStatus['name'], currentStatus['dataType'], currentStatus['requestDigit'], currentStatus['unit'], currentStatus['prefix'], currentStatus['postfix'])
			statusList.append(statusObject)
		return statusList

	def getStatus(self):
		return self._statusList

# generate sensor
class SensorFactory:
	def __init__(self, databaseGet):
		self.databaseGet = databaseGet
		self._sensorList = self.produceSensorsFromDatabase()

	def produceSensorsFromDatabase(self):
		sensors = self.databaseGet.getSensor()
		sensorList = []
		for sensor in sensors:
			sensorList.append(Sensor(sensor['name'], sensor['rate'], sensor['id']))
		return sensorList

	def getSensors(self):
		return self._sensorList

# manages objects sensor and status. 
class ObjectManager:
	def __init__(self, dataConnector):
		self._dataConnector = dataConnector
		self.buildConfiguration()

	def buildConfiguration(self):
		self._sensorList = SensorFactory(self._dataConnector).getSensors()
		self._statusList = StatusFactory(self._dataConnector, self._sensorList).getStatus()

	def disconnectSensors(self):
		for sensor in self._sensorList:
			sensor.disconnect()

	def getSensorList(self):
		return self._sensorList

	def getStatusList(self):
		return self._statusList

	def addStatus(self, statusDict):
		# write status into database and build configuration again
		myId = self._dataConnector.getHighestId() + 1
		statusDict['id'] = myId
		self.disconnectSensors()
		self._dataConnector.addStatus(statusDict)
		self.buildConfiguration()

# Interface for Statusinstance
class GetInterface:
	def __init__(self, objectManager):
		# assign the object manager
		self.objectManager = objectManager
	
	def _notFound(self):
		return {'message': 'Did not find Sensor.'}

	# get a status by a given id
	def getStatusById(self, id, requestSensor = True):
		for status in self._getStatusFromManager():
			if(status.getStatusId() == id):
				return status.getFormattedStatus(requestSensor)
		return self._notFound()

	# get a status by a name
	def getStatusByName(self, name, requestSensor = True):
		for status in self._getStatusFromManager():
			# take lower name
			if(status.getStatusName().lower() == name.lower()):
				return status.getFormattedStatus(requestSensor)
		return self._notFound()

	def getStatusList(self, requestSensor = True):
		_return = []
		for status in self._getStatusFromManager():
			_return.append(status.getFormattedStatus(requestSensor))
		return _return

	def _getStatusFromManager(self):
		return self.objectManager.getStatusList()

# Interface for writing Status and Sensors
class WriteInterface:
	# get interface for reloading the configuration
	def __init__(self, objectManager):
		self.objectManager = objectManager

	def addStatus(self, statusDict):
		self.objectManager.addStatus(statusDict)