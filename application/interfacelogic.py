from flask import Flask, jsonify, request, render_template
from flask_ask import Ask, statement, question
import statuslogic


class Main:
    def __init__(self):
        self.manager = statuslogic.Manager()

manager = Main().manager

# Flask Application
app = Flask(__name__)

"""
ALEXA CONFIGURATION
"""
ask = Ask(app, '/ask')


# First Start of Alexa
@ask.launch
def connection():
    return question("Welchen Status moechtest du wissen?")


# Ask Intent for Status Intent
@ask.intent('StatusIntent')
def get_status(status_name, status_id):
    current_status = None
    if status_name != '?' and status_name is not None:
        current_status = manager.get_status('name', status_name, True)
    elif status_id != '?' and status_id is not None:
        current_status = manager.get_status('id', status_id, True)
    else:
        return question("Bitte gib eine ID-Nummer oder einen Namen vom Statusgeraet an.")
    if not current_status:
        return question("Sorry, konnte ich nicht finden.")
    if current_status['value'] is False:
        return question("Es gibt ein Problem mit dem Sensor. Versuche es erneut.")
    # if there is a bool, use the unit and split it
    if current_status.get('data_type') == 'bool':
        return statement(current_status.get('prefix') + " " +
                        current_status.get('unit').split('|')[int(current_status.get('value'))] + " " +
                        current_status.get('postfix'))
    return statement(current_status.get('prefix') + " " + current_status.get('value') + " " + current_status.get('unit')
                    + " " + current_status.get('postfix'))

"""
API CONFIGURATION
"""


@app.route('/api/status', methods=['GET', 'POST', 'DELETE'])
def get_status_list():
    if request.method == 'GET':
        request_value = False
        if str(request.args.get('request')) == "1":
            request_value = True
        if request.args.get('name'):
            return jsonify(manager.get_status('name', request.args.get('name'), request_value))
        if request.args.get('id'):
            return jsonify(manager.get_status('id', request.args.get('id'), request_value))
        return jsonify(manager.get_status())
    elif request.method == 'POST':
        return jsonify(manager.add_status(StatusModel().make_dictionary(request.form)))
    elif request.method == 'DELETE':
        if request.args.get('name'):
            return jsonify(manager.remove_status('name', request.args.get('name')))
        if request.args.get('id'):
            return jsonify(manager.remove_status('id', request.args.get('id')))
        return {'message': 'could not delete status because you have given no attributes name or id'}


@app.route('/api/sensor', methods=['GET', 'POST', 'DELETE'])
def get_sensor_list():
    if request.method == 'GET':
        if request.args.get('name'):
            return jsonify(manager.get_sensor('name', request.args.get('name')))
        if request.args.get('id'):
            return jsonify(manager.get_sensor('id', request.args.get('id')))
        return jsonify(manager.get_sensor())
    elif request.method == 'POST':
        return jsonify(manager.add_sensor(SensorModel().make_dictionary(request.form)))
    elif request.method == 'DELETE':
        return jsonify(manager.remove_sensor(request.args.get('id')))
"""
HTML
"""


@app.route('/')
def index():
    return render_template('index.html')


class Model(object):
    def __init__(self, attributes):
        self.attributes = attributes

    def make_dictionary(self, external_dictionary):
        my_return = {}
        for value in self.attributes:
            my_return[value] = external_dictionary.get(value)
        return my_return


class SensorModel(Model):
    def __init__(self):
        super(SensorModel, self).__init__(['name', 'port', 'rate'])


class StatusModel(Model):
    def __init__(self):
        super(StatusModel, self).__init__(['data_type', 'name', 'postfix', 'prefix', 'request_digit', 'sensor', 'unit'])
"""
RUN THE APPLICATION
"""
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
