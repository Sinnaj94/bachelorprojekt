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
		# create the statusinterface with given statusfactory
		self.statusInterface = statuslogic.StatusInterface(statuslogic.StatusFactory(self.getDataConnector).getSensors())
		time.sleep(1)
		print(self.statusInterface.getStatusByName("briefkasten"))

Main()