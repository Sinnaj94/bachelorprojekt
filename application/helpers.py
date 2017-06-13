import json
import os

# JSON HELPERS ----

# create a user setting based on the default settings
def createJson(_filename):
	_current_path = os.path.dirname(_filename)
	_current_file = os.path.basename(_filename)
	try:
		os.makedirs(_current_path)
	except (OSError):
		pass
	finally:
		_temp_object= loadJson(os.path.join('configuration',_current_file))
		print(_temp_object)
		saveJson(_filename, _temp_object)
		return _temp_object


# Load the JSON file
def loadJson(_filename):
	try:
		with open(_filename) as f:
			data = json.load(f)
			return data
	except (ValueError, IOError) as e:
		# create file if not found and return
		return createJson(_filename)

# Save the JSON file
def saveJson(_filename, _object):
	with open(_filename, 'w') as f:
		json.dump(_object, f, indent=4)
		return True

# --- JSON HELPERS

# API HELPERS ----

# check if arguments are given
def argsGiven(_args):
	print(_args)
	for key, value in _args.iteritems():
		if value:
			return True
	return False

# return plugs with given arguments
def getObjectsWithGivenArgs(_args, _object):
	_return = []
	for key, value in _args.iteritems():
		if value:
			for item in _object:
				for key_T, value_T in item.iteritems():
					if(value == value_T):
						_return.append(item)
	return _return

#	remove plugs with given arguments 
def deleteObjectById(_id, _object):
	current_index = -1;
	toDelete = None
	for item in _object:
		current_index+=1;
		if(int(item['id']) == int(_id)):
			toDelete = current_index
	if toDelete is not None:
		_object.pop(toDelete)
	return _object

# get max id
def getMaxValue(_name, _object):
	biggest = 1
	for item in _object:
		print(item)
		if(int(item[_name])) > biggest:
			biggest = int(item[_name])
	return biggest

#---- API HELPERS