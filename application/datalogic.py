import json
from shutil import copyfile
import os
import sys
import serial
import threading
import time


class DataConnector:
    def __init__(self):
        """
        Constructor
        :param database: The Database object
        """
        self._database = Database()

    def get_status(self, status_id=None):
        """
        Return statusconfiguration
        :param status_id: If given, return Status with status_id
        :return: Return statusconfiguration with optional id
        """
        return self._database.get_configuration('status_list', status_id)

    def get_sensor(self, sensor_id=None):
        """
        Return sensorconfiguration
        :param sensor_id: If given, return Sensor with sensor_id
        :return: Return sensorconfiguration with optional id
        """
        return self._database.get_configuration('sensor_list', sensor_id)

    def add_sensor(self, sensor_dict):
        """
        Add sensor to Configuration
        :param sensor_dict: Sensor Object in dictionary form
        """
        self._database.write_configuration('sensor_list', sensor_dict, True)

    def add_status(self, status_dict):
        """
        Add status to Configuration
        :param status_dict: Status Object in dictionary form
        """
        self._database.write_configuration('status_list', status_dict, True)

    def replace_status_list(self, status_list):
        """
        Save Statusdictionary to Configuration and overwrite it, but only if it is a list
        :param status_list: StatusList Serialized Object
        :return: Success
        """
        if isinstance(status_list, list):
            self._database.write_configuration('status_list', status_list, False)
            return True
        return False

    def replace_sensor_list(self, sensor_list):
        """
        Save SensorList to configuration and overwrite it, but only if it is a list
        :param sensor_list: SensorList Serialized Object
        :return: Success
        """
        if isinstance(sensor_list, list):
            self._database.write_configuration('sensor_list', sensor_list, False)
            return True
        return False


class SensorConnection(object):
    """
    Sensor item
    """
    def __init__(self, port, rate):
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
        self.thread_end = False
        try:
            self.start_listening_thread()
        except(KeyboardInterrupt, SystemExit):
            self.thread_end = True
        self.request_done = False

    def disconnect(self):
        """
        Close the Serial connection.
        """
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
        while self.serial is not None or self.thread_end:
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


class Database:
    def __init__(self, base="configuration", user_base="configuration/user", filename="database.json"):
        """
        Constructor for Database
        :param base: Base folder, where the standard configuration lies
        :param userbase: User folder, where the user configuration lies
        :param filename: Filename
        """
        self.base = base
        self.user_base = user_base
        self.filename = filename
        self._dataOperations = DataOperations(self.base, self.user_base, self.filename)

    def get_configuration(self, key=None, my_id=None):
        """
        Return Configuration from DB with given args
        :param args: Arguments
        :return: Configuration with given Arguments
        """
        my_list = self._dataOperations.return_configuration(key)
        if not my_id:
            return my_list
        for item in my_list:
            if my_id == item['id']:
                return item
        return None

    def write_configuration(self, key, value, append_array=False):
        """
        Write Configuration to Database by appending or replacing
        :param key: Key of Database
        :param value: Value to write to Database
        :param append_array: If this is true, append to an Array in the Database
        """
        if append_array:
            self._dataOperations.append_value(key, value)
        else:
            self._dataOperations.overwrite_value(key, value)

    def create_data_connector(self):
        return DataConnector(self)


class DataOperations:
    """
    Execute Privimitive File Operations
    """
    def __init__(self, base, user_base, my_file):
        """
        Constructor
        :param base: Folder for standard Configuration
        :param user_base: User Folder
        :param my_file: Filename
        """
        self._data = None
        self.base = base
        self.user_base = user_base
        self.my_file = my_file
        self.base_file = os.path.join(self.base, self.my_file)
        self.user_base_file = os.path.join(self.user_base, self.my_file)
        self.create_database()

    def update_data(self):
        self._data = self.load_data()

    def load_data(self):
        """
        Load Data from File
        :return: Dictionary with file content
        """
        with open(self.user_base_file) as infile:
            return json.load(infile)

    def user_prompt_exit(self, message):
        user_input = None
        while user_input != 'y' and user_input != 'n':
            print(message)
            user_input = raw_input().lower()
        if user_input == 'y':
            print("Restoring Default Database")
            self.create_database(True)
        elif user_input == 'n':
            print("Exiting")
            sys.exit()

    def save_data(self, data):
        """
        Save Data
        :param data: Data to Save
        """
        with open(self.user_base_file, 'w') as outfile:
            json.dump(data, outfile, indent=2)

    def create_database(self, overwrite=False):
        """
        Create the filesystem for the database
        :param overwrite: overwrite the Database
        :return:
        """
        self.create_folder(self.user_base)
        if not os.path.isfile(self.user_base_file) or overwrite:
            copyfile(self.base_file, self.user_base_file)
        try:
            self.update_data()
        except ValueError:
            self.user_prompt_exit("There was a Problem with the Database (" + self.user_base_file + "). Do you want to restore the Default Database? (Y/N)")


    def create_folder(self, folder_name):
        """
        Create a folder, if not existant
        :param folder_name: Folder Name
        """
        try:
            os.makedirs(os.path.join(folder_name))
        except(OSError):
            pass

    def return_configuration(self, key=None):
        """
        Return data
        :param key: Key that should be returned
        :return:
        """
        try:
            if not key:
                return self._data
            return self._data[key]
        except KeyError:
            return False

    def overwrite_value(self, key, value, save=True):
        """
        Overwrite a value of a key
        :param key: Key
        :param value: Data that should be overwritten
        :param save: Save To Database, default is true
        """
        self._data[key] = value
        if save:
            self.save_data(self._data)

    def append_value(self, key, value, save=True):
        """
        Append a value to an array
        :param key: Key array
        :param value: Appended Data
        :param save: Save to Database, default is true
        """
        self._data[key].append(value)
        if save:
            self.save_data(self._data)
