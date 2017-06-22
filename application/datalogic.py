import json
from shutil import copyfile
import os
from collections import defaultdict
### INTERFACES 
# connector to get values out of database and to write values into it
class DataConnector:
	# initialize DatabaseGet with given database
	def __init__(self, database):
		self._database = database

	# get whole database
	def getData(self, args):
		return self._database.getConfiguration(args)

	# returns integer of status with highest id
	def getHighestId(self, sensor = False):
		statusList = self.getStatus()
		if(sensor):
			statusList = self.getSensor()
		highest = -1
		for status in statusList:
			if(status['id'] > highest):
				highest = status['id']
		return highest

	# gets status of database. if no status id given, return all
	def getStatus(self, statusId = None):
		statusList = self._database.getConfiguration('statusList')
		if(not statusId):
			return statusList
		for status in statusList:
			if(statusId == status['id']):
				return status
		return None

	def getSensor(self, sensorId = None):
		sensorList = self._database.getConfiguration('sensorList')
		if(not sensorId):
			return sensorList
		for sensor in sensorList:
			if(sensorId == sensor['id']):
				return status
		return None

	def addSensor(self, sensorDict):
		self._database.writeConfiguration('sensorList', statusDict, True)

	def addStatus(self, statusDict):
		self._database.writeConfiguration('statusList', statusDict, True)

# Database
class Database:	
	def __init__(self, base = "configuration", userbase = "configuration/user", file = "database.json"):
		self.base = base
		self.file = file
		self.userbase = userbase
		self._dataOperations = DataOperations(base, userbase, file)
		self._dataOperations.createDatabase()

	# get configuration with optional given args. args can be a string or an array of strings, that iterates through the dictionary
	def getConfiguration(self, args = None):
		return self._dataOperations.returnConfiguration(args)

	def writeConfiguration(self, key, value, appendArray=False):
		print(appendArray)
		if(appendArray):
			self._dataOperations.appendToArray(key, value)
		else:
			self._dataOperations.replaceValue(key, value)
		#return self._dataOperations.writeConfiguration(args, value)

# Primitive Data Operations: Level 4
class DataOperations:
	def __init__(self, base = "configuration", userbase = "configuration/user", file = "database.json"):
		self.base = base
		self.userbase = userbase
		self.file = file
		self.basefile = os.path.join(self.base, self.file)
		self.userbasefile = os.path.join(self.userbase, self.file)

	def makeFolder(self):
		# Creates the Database based on standard database, if not existent yet.
		try:
			# create folder
			os.makedirs(os.path.join(self.userbase))
		except(OSError):
			print("Did not create Folder, because already existing.")
			pass

	def createDatabase(self, overwrite=False):
		self.makeFolder()
		# copy standard database to user database, if user database if not existant
		if(not os.path.isfile(self.userbasefile) or overwrite):
			copyfile(self.basefile, self.userbasefile)
		else:
			print("Did not create file, because already existing")

	def keyError(self):
		return {'error': 'no data matching'}

	def returnConfiguration(self, args = None):
		# store json in temporary object
		with open(self.userbasefile) as f:
			data = json.load(f)
			# if there are no arguments given, give all data
			try:
				if(not args):
					return data
				# if it is list, suppose that args are in array form
				if(isinstance(args, list)):
					return self._getByGivenArgs(args, data)
				return data[args]
			except(KeyError):
				return self.keyError()

	def appendToArray(self, key, value):
		# open database temporary
		with open(self.userbasefile) as f:
			data = json.load(f)
			data[key].append(value)
		# save data to database finally
		self.saveToDatabase(data)
		return True

	def appendToArray(self, key, value):
		# open database temporary
		with open(self.userbasefile) as f:
			data = json.load(f)
			data[key] = value
		# save data to database finally
		self.saveToDatabase(data)
		return True

	def saveToDatabase(self, data):
		with open(self.userbasefile, 'w') as outfile:
			json.dump(data, outfile, indent=2)
			return True

	def _setByGivenArgs(self, args, data, value):
		print("not implemented")
		return None


	def _getByGivenArgs(self, args, data):
		# nested dict with multiple args in array form
		current_data = data
		for arg in args:
			current_data = current_data[arg]
		return current_data