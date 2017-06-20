from flask import Flask, render_template
from flask_restful import abort, Api, Resource
from flask_ask import Ask, statement


class MobileApi:
	def __init__(self, statusInterface, configurationInterface, webConnector, path):
		self.statusInterface = statusInterface
		self.configurationInterface = configurationInterface
		self.api = Api(webConnector.app, path)
		self.addResources()

	def getStatus(self, id = None, name = None):
		return None

	def returnError(self,message="An error occured"):
		return {'error': message}

	def addResources(self):
		self.api.add_resource(self.Default, '/')
		self.api.add_resource(self.StatusList, '/status', resource_class_kwargs = {"statusInterface": self.statusInterface})
		self.api.add_resource(self.StatusById, '/status/id/<int:statusId>', resource_class_kwargs = {"statusInterface": self.statusInterface})
		self.api.add_resource(self.StatusByName, '/status/name/<string:statusName>', resource_class_kwargs = {"statusInterface": self.statusInterface})

		
	# returned resources
	class Default(Resource):
		def get(self):
			return {'version':'1.0', 'name': 'Sensor API', 'author': 'Jannis Jahr'}

	class StatusList(Resource):
		def __init__(self, **class_kwargs):
			self.statusInterface = class_kwargs['statusInterface']
		def get(self):
			return self.statusInterface.getStatusList()

	class StatusById(Resource):
		def __init__(self, **class_kwargs):
			self.statusInterface = class_kwargs['statusInterface']
		def get(self, statusId):
			return self.statusInterface.getStatusById(statusId)

	class StatusByName(Resource):
		def __init__(self, **class_kwargs):
			self.statusInterface = class_kwargs['statusInterface']
		def get(self, statusName):
			return self.statusInterface.getStatusByName(statusName)




class SpeechApi:
	def __init__(self, statusInterface, webConnector, path):
		self.statusInterface = statusInterface
		# using flask ask api
		self.ask = Ask(webConnector.app, path)
	
	# build ask intents
	@self.ask.intent('StatusIntent')
	def statusById(statusId, statusName):
		return "Hello World."


class WebConnector:
	def __init__(self, debug=False, host='0.0.0.0'):
		self.name = 'server'
		self.app = Flask('server')
		self.debug = debug
		self.host = host
		
	def startServing(self):
		print("Starting to serve")
		self.app.run(debug=self.debug, host=self.host)

app = Flask(__name__)
ask = Ask(app, '/ask')

@ask.intent('StatusIntent')
def hello():
    return statement('Hallo Johannes wie geht es dir?')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")