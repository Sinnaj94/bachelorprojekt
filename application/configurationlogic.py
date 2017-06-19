from datalogic import DatabaseWrite

class Configuration:
	def __init__(self, databaseWrite):
		self.databaseWrite = databaseWrite

	# status: Status object
	def addStatus(self, status):
		self.databaseWrite.addStatus(status)

