from datalogic import DataConnector, SensorConnection


class Identifiable(object):
    """
    Abstract class for calling name and id of an object
    """
    def __init__(self, my_id, name):
        self.my_id = my_id
        self.name = name

    def set_id(self, my_id):
        self.my_id = my_id

    def set_name(self, name):
        self.name = name

    def get_id(self):
        """
        Return ID
        :return: ID
        """
        return self.my_id

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


class Sensor(SensorConnection, Serializable, Identifiable):
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
        super(Sensor, self).__init__(port, rate)
        self.my_id = my_id
        self.name = name

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

    def append_to_list(self, obj):
        """
        Append a List or a single item to the list
        :param obj: List or Object
        """
        if isinstance(obj, list):
            for my_item in obj:
                self.my_list.append(my_item)
        else:
            self.my_list.append(obj)

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

    def produce_from_multiple_entries(self, obj_array):
        """
        Produce
        :param obj_array:
        :return:
        """
        for obj in obj_array:
            self.produce_from_single_entry(obj)

    def produce_from_single_entry(self, obj):
        """
        Produce from single entry. can be overwritten when using classes
        :param obj: Object that is appended
        :return:
        """
        # check if there is an id, otherwise generate it
        if not obj.get_id():
            obj.set_id(self.get_highest_id() + 1)
        self.append_to_list(obj)

    def remove_by_attribute(self, key, value):
        """
        Remove Key by attribute with a key value pair
        :param key: Key
        :param value: Value
        :return: Number of removed entries
        """
        removed = []
        # build list that should be removed
        for obj in self.my_list:
            if str(obj.serialize().get(key)) == str(value):
                removed.append(obj)
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
        for obj in self.my_list:
            if str(obj.serialize()[key]) == str(value):
                my_return.append(obj.serialize())
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
        if not sensor_dictionary.get('port') or not sensor_dictionary.get('rate'):
            return False
        sensor_object = Sensor(sensor_dictionary.get('port'), sensor_dictionary.get('rate'), sensor_dictionary.get('id'), sensor_dictionary.get('name'))
        super(SensorList, self).produce_from_single_entry(sensor_object)
        return self.my_list

    def save_to_remove(self, my_id, status_list):
        selected_sensor = self.get_by_attribute('id', my_id)[0]
        for status in status_list:
            if status['sensor'] == selected_sensor['id']:
                return False
        return True

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
    def __init__(self, save_to_database=True):
        self._data_connector = DataConnector()
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

    def error_with_status(self):
        return {'message': 'There has been an Error with the Status. The Sensor is probably configured wrong or idle.'}

    def get_status(self, key=None, value=None, request_status=False):
        if key is None:
            return self.status_list.serialize()
        if request_status:
            return self.status_list.get_current_status(key, value)
        return self.status_list.get_by_attribute(key, value)

    def get_sensor(self, key=None, value=None):
        if key is None:
            return self.sensor_list.serialize()
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

    def add_sensor(self, sensor_dictionary):
        """
        Add a Single Sensor
        :param sensor_dictionary: Status in Dictionary Form
        """
        self.sensor_list.produce_from_single_entry(sensor_dictionary)
        if self.save_to_database:
            self._data_connector.replace_sensor_list(self.sensor_list.serialize())
        return self.sensor_list.serialize()

    def remove_sensor(self, my_id):
        """
        Remove Value with specific key value pair
        :param key: key
        :param value: value
        :return:
        """
        if not self.sensor_list.save_to_remove(my_id, self.status_list.serialize()):
            return {'message': 'could not remove sensor, because it has active status items'}
        self.sensor_list.remove_by_attribute('id', my_id)
        if self.save_to_database:
            self._data_connector.replace_sensor_list(self.sensor_list.serialize())
        return self.sensor_list.serialize()
