from flask import Flask, render_template
from flask_restful import reqparse, abort, Api, Resource
from flask_ask import Ask, statement

class MobileApi:
	def __init__(self, statusInterface, configurationInterface, webConnector):
		self.statusInterface = statusInterface
		self.configurationInterface = configurationInterface
		self.api = Api(webConnector.app, '/api')
		self.addResources()

	def getStatus(self, id = None, name = None):
		return None

	def returnError(self,message="An error occured"):
		return {'error': message}

	def addResources(self):
		self.api.add_resource(self.Default, '/')
		self.api.add_resource(self.Status, '/status/<int:statusId>', resource_class_kwargs = {"statusInterface": self.statusInterface})
		#self.api.add_resource(self.TodoNext, '/next', resource_class_kwargs={ 'smart_engine': 'smart_engine' })

	# return 
	class Default(Resource):
		def get(self):
			return {'version':'1.0', 'name': 'Sensor API', 'author': 'Jannis Jahr'}

	class Status(Resource):
		def __init__(self, **class_kwargs):
			self.statusInterface = class_kwargs['statusInterface']
		def get(self, statusId):
			return self.statusInterface.getStatusById(statusId)



class SpeechApi:
	def __init__(self, statusInterface, webConnector):
		self.statusInterface = statusInterface
		self.api = Ask(webConnector.app, '/ask')


class WebConnector:
	def __init__(self, debug=False, host='0.0.0.0'):
		self.name = 'server'
		self.app = Flask('server')
		self.debug = debug
		self.host = host
		
	def startServing(self):
		print("Starting to serve")
		self.app.run(debug=self.debug, host=self.host)