import statuslogic
import datalogic
import configurationlogic
import time
class Main:
	def __init__(self):
		# DATABASE
		# create database
		self.database = datalogic.Database()
		self.getDataConnector = datalogic.DatabaseGet(self.database)
		self.writeDataConnector = datalogic.DatabaseWrite(self.database)
		# STATUS
		# generate all status objects from database
		self.statusList = statuslogic.StatusFactory(self.getDataConnector)

Main()