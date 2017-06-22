from flask import Flask, render_template, jsonify
from flask_restful import abort, Api, Resource, reqparse
from flask_ask import Ask, statement, question
import statuslogic
import datalogic
import interfacelogic
import time
from flask_marshmallow import Marshmallow
class Main:
	def __init__(self):
		self.objectManager = statuslogic.ObjectManager(datalogic.DataConnector(datalogic.Database()))
		self.getInterface = statuslogic.GetInterface(self.objectManager)
		self.writeInterface = statuslogic.WriteInterface(self.objectManager)

connector = Main()

# Flask Application
app = Flask(__name__)
ask = Ask(app, '/ask')
api = Api(app, '/api')

# Build Ask (Alexa) intent
@ask.launch
def connection():
    return question("Welchen Status?")

@ask.intent('StatusIntent')
def getStatus(statusName, statusId):
	currentStatus = None
	if(statusName!='?' and statusName != None):
		currentStatus = connector.getInterface.getStatusByName(statusName)
	elif(statusId!='?' and statusId != None):
		currentStatus = connector.getInterface.getStatusById(int(statusId))
	else:
		return statement("Bitte gib eine ID-Nummer oder einen Namen vom Statusgeraet an.")
	if('message' in currentStatus):
		return statement("Der Status mit den gegebenen Parametern wurde nicht gefunden oder es trat ein Problem auf.")
	if(currentStatus['dataType'] == 'bool'):
		return statement(currentStatus['prefix'] + " " + currentStatus['unit'].split('|')[int(currentStatus['value'])] + " " + currentStatus['postfix'])
	return statement(currentStatus['prefix'] + " " + currentStatus['value']+ " " + currentStatus['unit'] + " " + currentStatus['postfix'])

# Builds JSON API
parser = reqparse.RequestParser()
parser.add_argument("unit")
parser.add_argument("prefix")
parser.add_argument("postfix")
parser.add_argument("sensor")
parser.add_argument("requestDigit")
parser.add_argument("name")
parser.add_argument("dataType")
class Default(Resource):
	def get(self):
		return jsonify({'version':'1.0', 'name': 'Sensor API', 'author': 'Jannis Jahr'})

class StatusList(Resource):
	def get(self):
		return jsonify(connector.getInterface.getStatusList(False))
	def post(self):
		args = parser.parse_args()
		connector.writeInterface.addStatus(args)
		
class Status(Resource):
	def get(self, statusSelector):
		if(statusSelector.isdigit()):
			return jsonify(connector.getInterface.getStatusById(int(statusSelector)))
		return jsonify(connector.getInterface.getStatusByName(statusSelector))

api.add_resource(Default, '/')
api.add_resource(StatusList, '/status')
api.add_resource(Status, '/status/<string:statusSelector>')
# Run the application
app.run(debug=False, host="0.0.0.0")