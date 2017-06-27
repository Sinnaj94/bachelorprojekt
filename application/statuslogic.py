import serial
import time
import threading
from datalogic import Database, DataConnector


class Identifiable(object):
    """
    Abstract class for calling name and id of an object
    """
    def __init__(self, my_id, name):
        self.my_id = my_id
        self.name = name

    def get_id(self):
        """
        Return ID
        :return: ID
        """
        return self.my_id

    def set_id(self, my_id):
        self.my_id = my_id

    def get_name(self):
        """
        Return Name
        :return: Name
        """
        return self.name


class Serializable(object):
    """
    Abstract class, where Serialize should be overwritten, otherwise you get an error
    """
    def serialize(self):
        raise NotImplementedError()


class Sensor(Identifiable, Serializable):
    """
    Sensor item
    """
    def __init__(self, port, rate, my_id, name):
        """
        Constructor
        :param port: Port, that pyserial should access
        :param rate: Baud Rate of Sensor
        :param my_id: Id of the Sensor
        """
        super(Sensor, self).__init__(my_id, name)
        self.port = port
        self.rate = rate
        self.serial = self.get_serial()
        self.thread = None
        self.status = None
        self.timeout = .1
        self.max_number_of_requests = 5
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
            return None

    def listen_to_changes(self):
        """
        Listen to a signal of the Sensor and write them into the status variable
        """
        while self.serial is not None:
            try:
                current_status = self.serial.readline()
                # only update status, if a line could be read
                if not current_status:
                    return False
                self.status = current_status.splitlines()[0]
                self.request_done = True
            except serial.SerialException:
                self.status = None

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
        if self.serial is not None:
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
        # make all requests0
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

    def get_id(self):
        return self.my_id

    def serialize(self):
        return {'id': self.my_id, 'port': self.port, 'rate': self.rate, 'name': self.name}


class Status(Identifiable, Serializable):
    """
    Status item
    """
    def __init__(self, my_id, sensor, name, data_type, request_digit, unit=None, prefix=None, postfix=None):
        super(Status, self).__init__(my_id, name)
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

    def get_id(self):
        return self.my_id

    def serialize(self, sensor_request=False):
        return_value = {'id': self.my_id, 'unit': self.unit, 'sensor': self.sensor.my_id, 'name': self.name,
                        'prefix': self.prefix, 'postfix': self.postfix, 'request_digit': self.request_digit,
                        'data_type': self.data_type}
        if sensor_request:
            return_value['value'] = self.sensor.make_status_request(self.request_digit)
        return return_value


class MyList(object):
    """
    Abstract Serializable List
    """
    def __init__(self):
        self.my_list = []

    def append_to_list(self, appended):
        """
        Append a List or a single item to the list
        :param appended: List or Object
        """
        if isinstance(appended, list):
            for my_item in appended:
                self.my_list.append(my_item)
        else:
            self.my_list.append(appended)

    def serialize(self):
        """
        Serialize Array with object in dictionary form
        :return: Serialized array
        """
        serialized = []
        for my_item in self.my_list:
            serialized.append(my_item.serialize())
        return serialized

    def get_list(self):
        """
        :return: Get current List
        """
        return self.my_list

    def produce_from_multiple_entries(self, array):
        """
        Produce
        :param array:
        :return:
        """
        for my_object in array:
            self.produce_from_single_entry(my_object)

    def produce_from_single_entry(self, my_object):
        """
        Produce from single entry. can be overwritten when using classes
        :param my_object: Object that is appended
        :return:
        """
        # check if there is an id, otherwise generate it
        if not my_object.get_id():
            my_object.set_id(self.get_highest_id() + 1)
        self.append_to_list(my_object)

    def remove_by_attribute(self, key, value):
        """
        Remove Key by attribute with a key value pair
        :param key: Key
        :param value: Value
        :return: Number of removed entries
        """
        removed = []
        # build list that should be removed
        for my_item in self.my_list:
            if str(my_item.serialize().get(key)) == str(value):
                removed.append(my_item)
        for removed_item in removed:
            self.my_list.remove(removed_item)
        return self.serialize()

    def get_highest_id(self):
        highest = -1
        for my_item in self.my_list:
            if my_item.get_id() > highest:
                highest = my_item.get_id()
        return highest

    def get_by_attribute(self, key, value):
        my_return = []
        for my_item in self.my_list:
            if str(my_item.serialize()[key]) == str(value):
                my_return.append(my_item.serialize())
        return my_return


class StatusList(MyList):
    """
    Manage Status in a List and add them
    """
    def __init__(self, sensor_list):
        super(StatusList, self).__init__()
        self.sensor_list = sensor_list

    def produce_from_single_entry(self, status_dictionary):
        """
        Overwriting method
        :param status_dictionary: Status in serialized form
        :return: Success
        """
        if status_dictionary.get('sensor') is None:
            return False
        sensor = self.sensor_list.get_sensors(int(status_dictionary.get('sensor')))
        if not sensor:
            return False
        status_object = Status(status_dictionary.get('id'), sensor, status_dictionary.get('name'), status_dictionary.get('data_type'), status_dictionary.get('request_digit'), status_dictionary.get('unit'), status_dictionary.get('prefix'), status_dictionary.get('postfix'))
        super(StatusList, self).produce_from_single_entry(status_object)
        return self.serialize()

    def get_current_status(self, key, value):
        my_return = []
        for my_status in self.my_list:
            if str(my_status.serialize()[key]) == str(value):
                my_return.append(my_status.serialize(True))
        return my_return


class SensorList(MyList):
    """
    Manage Sensors in a List and add them
    """
    def __init__(self):
        super(SensorList, self).__init__()

    def produce_from_single_entry(self, sensor_dictionary):
        sensor_object = Sensor(sensor_dictionary.get('port'), sensor_dictionary.get('rate'), sensor_dictionary.get('id'), sensor_dictionary.get('name'))
        super(SensorList, self).produce_from_single_entry(sensor_object)

    def get_sensors(self, my_id=None):
        """
        Get all Sensors
        :param my_id: If set, return Sensor with specific Id
        :return: Sensor optionally with specific ID
        """
        if my_id is None:
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
    def __init__(self, data_connector, save_to_database=True):
        self._data_connector = data_connector
        self.sensor_list = SensorList()
        self.status_list = StatusList(self.sensor_list)
        self.save_to_database = save_to_database
        self.produce_from_database()

    def produce_from_database(self):
        """
        Produce all Sensors and Status using data_connector
        """
        self.sensor_list.produce_from_multiple_entries(self._data_connector.get_sensor())
        self.status_list.produce_from_multiple_entries(self._data_connector.get_status())

    def get_status_and_request_sensor(self, key, value):
        """
        Get Status and Request the underlying sensor with an id
        :param my_id: Id
        :return: dictionary object with additional value or error
        """
        my_return = self.status_list.get_current_status(key, value)
        if not my_return:
            return self.error_with_status()
        return my_return

    def error_with_status(self):
        return {'message': 'There has been an Error with the Status. The Sensor is probably configured wrong or idle.'}

    def get_status_list(self):
        """
        :return: Dictionary of statuslist
        """
        return self.status_list.serialize()

    def get_sensor_list(self):
        """
        :return: Dictionary of sensorlist
        """
        return self.sensor_list.serialize()

    def get_status_by_attribute(self, key, value, request_status=False):
        if request_status:
            return self.get_status_and_request_sensor(key, value)
        return self.status_list.get_by_attribute(key, value)

    def get_sensor_by_attribute(self, key, value):
        return self.sensor_list.get_by_attribute(key, value)

    def add_status(self, status_dictionary):
        """
        Add a Single Status
        :param status_dictionary: Status in Dictionary Form
        :param save_to_database: Optionally save it to Database. Default is True
        """
        message = self.status_list.produce_from_single_entry(status_dictionary)
        if self.save_to_database:
            self._data_connector.replace_status_list(self.status_list.serialize())
        if not message:
            return {'message': 'could not create status, because sensor id is empty'}
        return message

    def remove_status(self, key, value):
        """
        remove status by key and value and save to database
        :param my_id: id of the sensor
        :return:
        """
        message = self.status_list.remove_by_attribute(key, value)
        if self.save_to_database:
            self._data_connector.replace_status_list(self.status_list.serialize())
        return message

    def remove_sensor(self, my_id):
        """
        Remove Value with specific key value pair
        :param key: key
        :param value: value
        :return:
        """
        number = self.sensor_list.remove_by_attribute('id', my_id)
        if self.save_to_database:
            self._data_connector.replace_sensor_list(self.sensor_list.serialize())
        return number

    def add_sensor(self, sensor_dictionary):
        """
        Add a Single Sensor
        :param sensor_dictionary: Status in Dictionary Form
        """
        self.sensor_list.produce_from_single_entry(sensor_dictionary)
        if self.save_to_database:
            self._data_connector.replace_sensor_list(self.sensor_list.serialize())
        return self.sensor_list.serialize()
