import json
from shutil import copyfile
import os

### INTERFACES 
# connector to get values out of database
class DatabaseGet:
	# initialize DatabaseGet with given database
	def __init__(self, database):
		self._database = database

	# get whole database
	def getData(self, args):
		return self._database.getConfiguration(args)

	# returns integer of status with highest id
	def getHighestId(self):
		statusList = self.getStatus()
		highest = -1
		for status in statusList:
			if(status['statusId'] > highest):
				highest = status['statusId']
		return highest

	# gets status of database. if no status id given, return all
	def getStatus(self, statusId = None):
		statusList = self._database.getConfiguration('statusList')
		if(not statusId):
			return statusList
		for status in _return:
			if(statusId == status['statusId']):
				return status
		return None


# connector to write values into database
class DatabaseWrite:
	def __init__(self, database):
		self._database = Database

	def writeData(self, args, value):
		return _database.writeConfiguration(args, value)

### INTERFACES

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

	def writeConfiguration(self, args, value):
		return self._dataOperations.writeConfiguration(args, value)

# Todo Put in data operations
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
					print("B")
				return data[args]
			except(KeyError):
				return self.keyError()

	def writeConfiguration(self, args, value):
		# open database temporary
		with open(self.userbasefile) as f:
			data = json.load(f)
			if(isinstance(args, list)):
				return True
			data[args] = value
		# save data to database finally
		self.saveToDatabase(data)
		return False

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

# TODO: rausnehmen am Ende
database = Database()
dataConnect = DatabaseGet(database)
print(dataConnect.getHighestId())