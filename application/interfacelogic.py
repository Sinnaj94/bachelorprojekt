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
		self.api.add_resource(, '/status')


class SpeechApi:
	def __init__(self, statusInterface, webConnector):
		self.statusInterface = statusInterface
		self.api = Ask(webConnector.app, '/ask')


class WebConnector:
	def __init__(self, debug=False, host='0.0.0.0'):
		self.app = Flask(__name__)
		self.debug = debug
		self.host = host
		
	def startServing(self):
		if __name__ == '__main__':
			self.app.run(debug=self.debug, host=self.host)


connector = WebConnector()
mobileApi = MobileApi(None, None, connector)
connector.startServing()
















#WebConnector()
#AskConnector("a",1,1)

"""
# - configuration variables and load json once
object_file = './configuration/user/objects.json'
conf_object = helpers.loadJson(object_file)
default = {}
# - Flask configuration
app = Flask(__name__)
# - ask configuration
ask = Ask(app, '/ask')
# parser variables
parser = reqparse.RequestParser()
parser.add_argument('id')
parser.add_argument('address')
parser.add_argument('name')
parser.add_argument('description')
parser.add_argument('category')



# - api configuration
api = Api(app, '/api')

# ASK CONFIGURATION ----

@ask.intent('HelloIntent')
def hello(firstname):
    text = render_template('hello', firstname=firstname)
    return statement(text).simple_card('Hello', text)

# ---- ASK CONFIGURATION

# API CONFIGURATION ----

# Outputs the Standard information
class Default(Resource):
	def get(self):
		return default

# Get the whole Status List
def abortIfNotExisting(status_id):
	abort(404, message="Status {} doesn't exist".format(status_id))

class StatusList(Resource):
	def get(self):
		args = parser.parse_args()
		# check if args are given and return the searchlist then
		if helpers.argsGiven(dict(args)):
			return helpers.getObjectsWithGivenArgs(dict(args), conf_object['statusList'])
		return conf_object['statusList']
	def post(self):
		args = parser.parse_args()
		# standard number is 1, so if there is no object in array, it doesnt try max function
		_id = helpers.getMaxValue('id', conf_object['statusList']) + 1
		_current_object = {'id': _id, 'address': args['address'], 'name': args['name'], 'description': args['description'], 'category': args['category']}
		conf_object['statusList'].append(_current_object)
		helpers.saveJson(object_file, conf_object)
		return _current_object

class Status(Resource):
	def get(self, status_id):
		_return = helpers.getObjectsWithGivenArgs({'id': int(status_id)}, conf_object['statusList']);
		if _return:
			return _return[0]
		else:
			abortIfNotExisting(status_id)
	def delete(self, status_id):
		_return = helpers.getObjectsWithGivenArgs({'id': int(status_id)}, conf_object['statusList']);
		if _return:
			_temp = helpers.deleteObjectById(status_id, conf_object['statusList']);
			conf_object['statusList'] = _temp
		else:
			abortIfNotExisting(status_id)
		helpers.saveJson(object_file, conf_object)
		return(conf_object)

# Actual Status-Interface
class Status_Get(Resource):
	def get(self, status_id):
		return 'abc'

class StatusObject(Resource):
	def get(self):
		return conf_object['configuration']['statusObject']

api.add_resource(Default,'/')
api.add_resource(StatusList, '/status')
api.add_resource(Status, '/status/<status_id>')
api.add_resource(Status_Get, '/status/<status_id>/get')
api.add_resource(StatusObject, '/configuration/statusobject')
# ---- API CONFIGURATION

# SETTINGS CONFIGURATION -

@app.route('/')
def index():
	return render_template('index.html', objects= conf_object)

# - SETTINGS CONFIGURATION

# SERVER CONFIGURATION -

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# - SERVER CONFIGURATION

"""