import serial
import subprocess
import time
import threading
from datalogic import Database, DataConnector
# TODO: Docs


class Sensor():
    """
    Sensor item
    """
    def __init__(self, port, rate, my_id):
        """
        Constructor
        :param port: Port, that pyserial should access
        :param rate: Baud Rate of Sensor
        :param my_id: Id of the Sensor
        """
        self.port = port
        self.rate = rate
        self.serial = self.get_serial()
        self.thread = None
        self.status = None
        self.timeout = .1
        self.max_number_of_requests = 5
        self.my_id = my_id
        self.start_listening_thread()
        self.request_done = False

    def disconnect(self):
        self.serial.close()

    def get_serial(self):
        """
        Build the Serial Configuration using pySerial
        :return: pySerial Object or None if not available
        """
        try:
            return serial.Serial(self.port, self.rate)
        except serial.SerialException:
            print("Serial Device on port " + self.port + " could not be connected.")
            self.connection_error = True
            return None

    def listen_to_changes(self):
        """
        Listen to a signal of the Sensor and write them into the status variable
        """
        while serial is not None:
            try:
                current_status = self.serial.readline()
                # only update status, if a line could be read
                if not current_status:
                    return False
                self.status = current_status.splitlines()[0]
                self.request_done = True
            except serial.SerialException:
                self.status = False

    def start_listening_thread(self):
        """
        start a subthread with listen_to_changes
        """
        self.thread = threading.Thread(target=self.listen_to_changes, args=())
        self.thread.daemon = True
        self.thread.start()

    def request_status_once(self, request_digit):
        """
        Request the status using a request digit
        :param request_digit: request digit as a char, that can be sent to arduino
        :return:
        """
        try:
            self.request_done = False
            self.serial.write(str(request_digit))
        except serial.SerialException:
            pass

    def make_status_request(self, request_digit):
        """
        Make multiple status request with a timeout
        :param request_digit: 
        :return: 
        """
        self.request_done = False
        number_of_requests = 0
        # make all requests
        while not self.request_done and number_of_requests < self.max_number_of_requests:
            # make a request and wait for a specific time
            self.request_status_once(request_digit)
            number_of_requests += 1
            time.sleep(self.timeout)
        if not self.request_done:
            return False
        return self.status

    def get_current_status(self, request_digit):
        """
        get the current status by making the statusrequest
        :param request_digit: char request digit, the pc should send to arduino
        :return: current status. if not given, it is false
        """
        return self.make_status_request(request_digit)

    def serialize(self):
        return {'id': self.my_id, 'port': self.port, 'rate': self.rate}


class Status:
    """
    Status item
    """
    def __init__(self, my_id, sensor, name, data_type, request_digit, unit=None, prefix=None, postfix=None):
        self.my_id = my_id
        self.name = name
        self.sensor = sensor
        self.prefix = prefix
        self.postfix = postfix
        self.data_type = data_type
        self.unit = unit
        self.request_digit = request_digit

    def request_status(self):
        """
        request the sensor with given request digit
        :return: sensor status
        """
        return self.sensor.get_current_status(self.request_digit)

    def serialize(self):
        return {'unit': self.unit, 'sensor': self.sensor.my_id, 'name': self.name, 'prefix': self.prefix,
                'postfix': self.postfix, 'request_digit': self.request_digit, 'data_type': self.data_type}


class MyList(object):
    """
    Abstract Serializable List
    """
    def __init__(self):
        self.my_list = []

    def append_to_list(self, appended):
        if isinstance(appended, list):
            for my_item in appended:
                self.my_list.append(my_item)
        else:
            self.my_list.append(appended)

    def serialize(self):
        serialized = []
        for my_item in self.my_list:
            serialized.append(my_item.serialize())
        return serialized

    def get_list(self):
        return self.my_list

    def produce_from_multiple_entries(self, array):
        for my_object in array:
            self.produce_from_single_entry(my_object)

    def produce_from_single_entry(self, my_object):
        self.append_to_list(my_object)


# generate status with including data from database
class StatusList(MyList):
    """
    Manage Status in a List and add them
    """
    def __init__(self, sensor_list):
        super(StatusList, self).__init__()
        self.sensor_list = sensor_list

    def produce_from_single_entry(self, status_dictionary):
        sensor = self.sensor_list.get_sensors(int(status_dictionary.get('sensor')))
        if not sensor:
            return False
        status_object = Status(status_dictionary.get('id'), sensor, status_dictionary.get('name'), status_dictionary.get('data_type'), status_dictionary.get('request_digit'), status_dictionary.get('unit'), status_dictionary.get('prefix'), status_dictionary.get('postfix'))
        super(StatusList, self).produce_from_single_entry(status_object)


class SensorList(MyList):
    """
    Manage Sensors in a List and add them
    """
    def __init__(self):
        super(SensorList, self).__init__()

    def produce_from_single_entry(self, sensor_dictionary):
        sensor_object = Sensor(sensor_dictionary.get('port'), sensor_dictionary.get('rate'), sensor_dictionary.get('id'))
        super(SensorList, self).produce_from_single_entry(sensor_object)

    def get_sensors(self, my_id = None):
        if not my_id:
            return self.my_list
        else:
            for sensor in self.my_list:
                if my_id == sensor.my_id:
                    return sensor
        return False


class Manager:
    """
    Manages Lists and used to create new Items in those Lists
    """
    def __init__(self, data_connector):
        self._data_connector = data_connector
        self.sensor_list = SensorList()
        self.status_list = StatusList(self.sensor_list)
        self.produce_from_database()

    def produce_from_database(self):
        """
        Produce all Sensors and Status using data_connector
        """
        self.sensor_list.produce_from_multiple_entries(self._data_connector.get_sensor())
        self.status_list.produce_from_multiple_entries(self._data_connector.get_status())

    def add_status(self, status_dictionary, save_to_database=True):
        self.status_list.produce_from_single_entry(status_dictionary)
        print(self.status_list.serialize())
        self._data_connector.replace_status_list(self.status_list.serialize())

    def add_sensor(self, sensor_dictionary):
        self.sensor_list.produce_from_single_entry(sensor_dictionary)



class GetInterface:
    def __init__(self, objectManager):
        # assign the object manager
        self.objectManager = objectManager

    def _notFound(self):
        return {'message': 'Did not find Sensor.'}

    # get a status by a given id
    def getStatusById(self, id, requestSensor = True):
        for status in self._getStatusFromManager():
            if(status.get_id() == id):
                return status.request_status(requestSensor)
        return self._notFound()

    # get a status by a name
    def getStatusByName(self, name, requestSensor = True):
        for status in self._getStatusFromManager():
            # take lower name
            if(status.getStatusName().lower() == name.lower()):
                return status.request_status(requestSensor)
        return self._notFound()

    def getStatusList(self, requestSensor = True):
        _return = []
        for status in self._getStatusFromManager():
            _return.append(status.request_status(requestSensor))
        return _return

    def _getStatusFromManager(self):
        return self.objectManager.getStatusList()


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