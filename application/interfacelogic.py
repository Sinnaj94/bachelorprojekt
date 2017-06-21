from flask import Flask, render_template
from flask_restful import abort, Api, Resource
from flask_ask import Ask, statement, question
import statuslogic
import datalogic
import configurationlogic
import interfacelogic
import time

class Main:
	def __init__(self):
		self.database = datalogic.Database()
		self.getDataConnector = datalogic.DatabaseGet(self.database)
		self.writeDataConnector = datalogic.DatabaseWrite(self.database)
		self.statusInterface = statuslogic.StatusInterface(statuslogic.StatusFactory(self.getDataConnector).getSensors())

connector = Main()

# Flask Application
app = Flask(__name__)
ask = Ask(app, '/ask')

@ask.launch
def connection():
    return question("Tach zamm. Frag den Status gern ab. Aber im Endeffekt juckt's niemandem.")

# Build Ask intents
@ask.intent('StatusIntent')
def getStatus(statusName, statusId):
	currentStatus = None
	if(statusName!='?' and statusName != None):
		currentStatus = connector.statusInterface.getStatusByName(statusName)
	elif(statusId!='?' and statusId != None):
		currentStatus = connector.statusInterface.getStatusById(int(statusId))
	else:
		return statement("Bitte gib eine ID-Nummer oder einen Namen vom Statusgeraet an.")
	try:
		currentStatus['message']
		return statement("Der Status mit den gegebenen Parametern wurde nicht gefunden oder es trat ein Problem auf.")
	except(KeyError):
		return statement(currentStatus['prefix'] + " " + currentStatus['value']+ " " + currentStatus['unit'] + " " + currentStatus['postfix'])

# Run the application
app.run(debug=False, host="0.0.0.0")