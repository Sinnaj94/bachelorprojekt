import statuslogic
import datalogic
import configurationlogic
import interfacelogic
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
		#print(self.statusInterface.getStatusByName("briefkasten"))
		# INTERFACE - PRESENTATION LOGIC
		# create the necessary web connector
		self.webConnector = interfacelogic.WebConnector()
		# instantiate mobilelogic
		self.mobileApi = interfacelogic.MobileApi(self.statusInterface, None, self.webConnector)
		# instantiate ask logic
		# TODO
		# start serving using the web connector
		self.webConnector.startServing()


Main()