import json
from shutil import copyfile
import os


class DataConnector:
    def __init__(self, database):
        """
        Constructor
        :param database: The Database object
        """
        self._database = database

    def get_data(self, args=None):
        """
        Access Database and return Dictionary with Configuration
        :param args: Optional args
        :return: Dictionary with Configuration
        """
        return self._database.get_configuration(args)

    def get_highest_id(self, sensor=False):
        """
        Return highest id of Status or Sensor
        :param sensor: If true, highest id of Sensor is given
        :return: Highest id of Status or Sensor
        """
        my_list = self.get_status()
        if sensor:
            my_list = self.get_sensor()
        highest = -1
        for list_entry in my_list:
            if my_list['id'] > highest:
                highest = list_entry['id']
        return highest

    def get_status(self, status_id=None):
        """
        Return statusconfiguration
        :param status_id: If given, return Status with status_id
        :return: Return statusconfiguration with optional id
        """
        status_list = self._database.get_configuration('statusList')
        if not status_id:
            return status_list
        for status in status_list:
            if status_id == status['id']:
                return status
        return None

    def get_sensor(self, sensor_id=None):
        """
        Return sensorconfiguration
        :param sensor_id: If given, return Sensor with sensor_id
        :return: Return sensorconfiguration with optional id
        """
        sensor_list = self._database.get_configuration('sensorList')
        if not sensor_id:
            return sensor_list
        for sensor in sensor_list:
            if sensor_id == sensor['id']:
                return sensor
        return None

    def add_sensor(self, sensor_dict):
        """
        Add sensor to Configuration
        :param sensor_dict: Sensor Object in dictionary form
        """
        self._database.write_configuration('sensorList', sensor_dict, True)

    def add_status(self, status_dict):
        """
        Add status to Configuration
        :param status_dict: Status Object in dictionary form
        """
        self._database.write_configuration('statusList', status_dict, True)

    def remove_status(self, status_dict):
        """
        Remove Status from Configuration
        :param status_dict: status object in dictionary form
        :return:
        """
        try:
            self._database.remove_configuration('statusList', ['id', status_dict['id']])
            return True
        except KeyError:
            return False

    def replace_status_list(self, status_list):
        """
        Save Statusdictionary to Configuration and overwrite it
        :param status_list: Statuslist in array form
        :return:
        """
        self._database.write_configuration('statusList', status_list, False)


class Database:
    def __init__(self, base="configuration", userbase="configuration/user", filename="database.json"):
        """
        Constructor for Database
        :param base: Base folder, where the standard configuration lies
        :param userbase: User folder, where the user configuration lies
        :param filename: Filename
        """
        self.base = base
        self.user_base = userbase
        self.filename = filename
        self._dataOperations = DataOperations(self.base, self.user_base, self.filename)
        self._dataOperations.create_database()

    def get_configuration(self, args=None):
        """
        Return Configuration from DB with given args
        :param args: Arguments
        :return: Configuration with given Arguments
        """
        return self._dataOperations.return_configuration(args)

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


# Class for executing Primitive Data Operations
class DataOperations:
    def __init__(self, base, user_base, my_file):
        """
        Constructor
        :param base: Folder for standard Configuration
        :param user_base: User Folder
        :param my_file: Filename
        """
        self.base = base
        self.user_base = user_base
        self.my_file = my_file
        self.base_file = os.path.join(self.base, self.my_file)
        self.user_base_file = os.path.join(self.user_base, self.my_file)
        self._data = self.load_data()

    def load_data(self):
        with open(self.user_base_file) as infile:
            return json.load(infile)

    def save_data(self, data):
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
        else:
            print("Did not create file, because already existing and not to be overwritten.")

    def create_folder(self, folder_name):
        try:
            os.makedirs(os.path.join(folder_name))
        except(OSError):
            print("Did not create Folder, because already existing.")
            pass

    def return_configuration(self, key=None):
        try:
            if not key:
                return self._data
            return self._data[key]
        except KeyError:
            return False

    def overwrite_value(self, key, value, save=True):
        self._data[key] = value
        if save:
            self.save_data(self._data)

    def append_value(self, key, value, save=True):
        self._data[key].append(value)
        if save:
            self.save_data(self._data)

dat_con = DataConnector(Database())
dat_con.add_status("Test")
