import json
from shutil import copyfile
import os

class Database:	
	def __init__(self, base = "configuration", userbase = "configuration/user", file = "database.json"):
		self.base = base
		self.file = file
		self.userbase = userbase
		self.dataOperations = DataOperations(base, userbase, file)
		self.dataOperations.createDatabase()

# Todo Put in data operations
class DataOperations:
	def __init__(self, base, userbase, file):
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


		
data = Database()