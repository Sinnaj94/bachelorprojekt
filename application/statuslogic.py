import serial
import subprocess
import time
import threading
from datalogic import DataConnector


# Sensor: Allows connection to a hardware Sensor
class Sensor:
    # name = name of usb host of sensor
    # rate = baud rate of sensor
    def __init__(self, port, rate, id):
        self.port = port
        self.rate = rate
        self.thread = None
        self.connection_error = False
        self.serial = self.get_serial()
        self.status = None
        self.thread = None
        self.statusRequestPending = False
        self.waitTime = .1
        self.maximalRequests = 5
        self.id = id
        self.start_listening_thread()

    def disconnect(self):
        self.connection_error = True
        self.serial.close()

    # build serial connection to sensor
    def get_serial(self):
        try:
            return serial.Serial(self.port,self.rate)
        except serial.SerialException:
            print("Serial Device on port "+ self.port+ " could not be connected.")
            self.connection_error = True

    # listen to changes of sensor
    def listen_to_changes(self):
        # reads status and returns it when finished
        while(not self.connection_error):
            try:
                currentValue = self.serial.readline().splitlines()[0]
                if(currentValue):
                    self.statusRequestPending = False
                    self.status = currentValue
            except(serial.SerialException):
                currentValue = "Not available"

    # check if there was a connection error at the beginning
    def has_connection_error(self):
        return self.connection_error

    # starts listening thread to sensor
    def start_listening_thread(self):
        self.thread = threading.Thread(target=self.listen_to_changes, args=())
        self.thread.daemon = True
        self.thread.start()

    # requests the status by sending a byte to the hardware sensor
    def request_status_once(self, requestDigit):
        if not self.has_connection_error():
            self.statusRequestPending = True
            self.serial.write(str(requestDigit))

    # make multiple requests until answer is given
    # TODO: implement timeout
    def make_status_request(self, requestDigit):
        self.statusRequestPending = True
        currentRequest = 0
        while(self.statusRequestPending and currentRequest < self.maximalRequests):
            self.request_status_once(requestDigit)
            currentRequest+=1
            time.sleep(.1)
        if(self.statusRequestPending):
            return False
        return self.status

    # make a status request and return value
    def get_current_status(self, requestDigit):
        if(self.has_connection_error()):
            return False
        return self.make_status_request(requestDigit)

    def get_id(self):
        return self.id

    def to_dict(self):
        return {'id': self.id, 'name': self.port, 'rate': self.rate}


class Status:
    # sensor = sensor object
    # statusId = id of sensor - automatically generated
    def __init__(self, id, sensor, name, dataType, requestDigit, unit=None, prefix=None, postfix=None):
        if not id:
            self.id = self.generateStatusId()
        else:
            self.id = id
        if not name:
            self.name = "Statusgeraet_" + self.id
        else:
            self.name = name
        self.sensor = sensor
        self.prefix = prefix
        self.postfix = postfix
        self.dataType = dataType
        self.unit = unit
        self.requestDigit = requestDigit

    def getSensor(self):
        return self.sensor

    # return status configuration as dict object
    def toDict(self):
        return {'unit': self.unit, 'sensor': self.sensor.get_id(), 'name': self.name, 'prefix': self.prefix, 'postfix': self.postfix, 'requestDigit': self.requestDigit, 'dataType': self.dataType}

    # request sensor and format the status
    def getFormattedStatus(self, requestSensor = True):
        sensorStatus = None
        if(requestSensor):
            sensorStatus = self.sensor.get_current_status(self.requestDigit)
        return {'value': sensorStatus, 'name': self.name ,'prefix': self.prefix, 'postfix': self.postfix, 'id': self.id, 'dataType': self.dataType, 'unit': self.unit}

    def getStatusId(self):
        return self.id

    def getStatusName(self):
        return self.name

# generate status with including data from database
class StatusFactory:
    def __init__(self, databaseGet, sensorFactory):
        self.databaseGet = databaseGet
        self.sensorFactory = sensorFactory
        self._statusList = []
        self.produceFromDatabase()

    def produceFromDatabase(self):
        status = self.databaseGet.get_status()
        for currentStatus in status:
            self.produceFromSingleEntry(currentStatus)
        return self._statusList

    def produceFromSingleEntry(self, currentStatus):
        sensorObject = None
        for sensor in self.sensorFactory.getSensors():
            if(sensor.get_id() == int(currentStatus['sensor'])):
                sensorObject = sensor
        if(not sensorObject):
            print("Statusobject could not be added.")
            return False
        statusObject = Status(currentStatus['id'], sensorObject, currentStatus['name'], currentStatus['dataType'], currentStatus['requestDigit'], currentStatus['unit'], currentStatus['prefix'], currentStatus['postfix'])
        self._statusList.append(statusObject)

    def getStatus(self):
        return self._statusList


# generate sensor and manage them
class SensorFactory:
    def __init__(self, databaseGet):
        self.databaseGet = databaseGet
        self._sensorList = []
        self.produceFromDatabase()

    def produceFromDatabase(self):
        sensors = self.databaseGet.get_sensor()
        for sensor in sensors:
            self.produceFromSingleEntry(sensor)
        return self._sensorList

    def produceFromSingleEntry(self, currentSensor):
        sensorObject = Sensor(currentSensor['name'], currentSensor['rate'], currentSensor['id'])
        self._sensorList.append(sensorObject)

    def getSensors(self):
        return self._sensorList


# manages objects sensor and status. 
class ObjectManager:
    def __init__(self, dataConnector):
        self._dataConnector = dataConnector
        self.sensorFactory = SensorFactory(self._dataConnector)
        self.statusFactory = StatusFactory(self._dataConnector, self.sensorFactory)
        self.refreshValues()

    def refreshValues(self):
        self._sensorList = self.sensorFactory.getSensors()
        self._statusList = self.statusFactory.getStatus()

    def listToDict(self, myList):
        _return = []
        for item in myList:
            _return.append(item.to_dict())
        return _return

    def disconnectSensors(self):
        for sensor in self._sensorList:
            sensor.disconnect()

    def saveStatusListToDatabase(self):
        self._dataConnector.replace_status_list(self.listToDict(self._statusList))

    def getSensorList(self):
        return self._sensorList

    def getStatusList(self):
        return self._statusList

    def addStatus(self, statusDict):
        # write status into database and build configuration again
        statusDict['id'] = self._dataConnector.get_highest_id() + 1
        if(not self.statusFactory.produceFromSingleEntry(statusDict)):
            return False
        self.refreshValues()
        self.saveStatusListToDatabase()

    def replaceStatus(self, statusDict):
        # write status into database and build configuration again
        _return = self._dataConnector.replaceStatus(statusDict)
        self.reset()
        return _return

    def removeStatus(self, statusDict):
        # write status into database and build configuration again
        _return = self._dataConnector.remove_status(statusDict)
        self.reset()
        return _return

    def reset(self):
        self.disconnectSensors()
        self.buildConfiguration()


# Interface for Statusinstance
class GetInterface:
    def __init__(self, objectManager):
        # assign the object manager
        self.objectManager = objectManager

    def _notFound(self):
        return {'message': 'Did not find Sensor.'}

    # get a status by a given id
    def getStatusById(self, id, requestSensor = True):
        for status in self._getStatusFromManager():
            if(status.getStatusId() == id):
                return status.getFormattedStatus(requestSensor)
        return self._notFound()

    # get a status by a name
    def getStatusByName(self, name, requestSensor = True):
        for status in self._getStatusFromManager():
            # take lower name
            if(status.getStatusName().lower() == name.lower()):
                return status.getFormattedStatus(requestSensor)
        return self._notFound()

    def getStatusList(self, requestSensor = True):
        _return = []
        for status in self._getStatusFromManager():
            _return.append(status.getFormattedStatus(requestSensor))
        return _return

    def _getStatusFromManager(self):
        return self.objectManager.getStatusList()

# Interface for writing Status and Sensors
class WriteInterface:
    # get interface for reloading the configuration
    def __init__(self, objectManager):
        self.objectManager = objectManager

    def addStatus(self, statusDict):
        self.objectManager.add_status(statusDict)

    def removeStatus(self, statusDict):
        return self.objectManager.remove_status(statusDict)

    def replaceStatus(self, statusDict):
        return self.objectManager.replaceStatus(statusDict)