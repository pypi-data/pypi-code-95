# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC
import os
from pathlib import Path
import time
import enum
import socket
try:
    import portalocker
except Exception as e:
    print("Portalocker isn't installed. User health check will be disabled. Exception:{0}", str(e))


class Simulator(ABC):
    """Defines methods for interacting with runtime simulator instances.

    Simulators are processes that run on a compute target and listen on a process specific port.
    Instances of this class hold the information necessary to connect to a simulator during execution of
    a reinforcement learning experiment.
    This class is typically referenced and used during experiment execution and not during control plane operations
    in the SDK.

    :param simulator_id: The system assigned ID for an instance of a simulator.
    :type simulator_id: str
    :param ip_address: The IP address where the simulator instance is running.
    :type ip_address: str
    :param port: The port where the simulator instance is listening for connections.
    :type port: str
    """
    # The file extension used in simulator match making
    _FILE_EXTENSION = ".sim"
    _HEALTH_CHECK_PREFIX = "HealthCheck:"

    class HealthStatus(enum.Enum):

        """
        Indicates the health status of a Simulator.
        """
        starting = 0
        alive = 1
        dead = 2
        restart = 3
        error = 4

    def __init__(self, simulator_id, ip_address, port):
        """Initializes a simulator reference with its id, IP address and port.

        :param simulator_id: The system assigned ID for an instance of a simulator.
        :type simulator_id: str
        :param ip_address: The IP address where the simulator instance is running.
        :type ip_address: str
        :param port: The port where the simulator instance is listening for connections.
        :type port: str
        """
        self.id = simulator_id
        self.port = port

        if ip_address is None or ip_address is "":
            self.ip_address = socket.gethostbyname(socket.gethostname())
        else:
            self.ip_address = ip_address

    def __repr__(self):
        return "<Simulator id:%s ip_address:%s port:%s>" % (self.id, self.ip_address, self.port)

    @staticmethod
    def get_simulators(min_count=1, timeout_seconds=None, raise_on_timeout=True):
        """Get the list of simulators that are running for the currently executing run.

        By specifying `min_count`, the method will not return until `min_count` number of simulators are running
        or until `timeout_seconds` has elapsed.

        :param min_count: When this parameter is specified, the method will not return until `min_count`
            simulators have started running.
        :type min_count: int
        :param timeout_seconds: If `min_count` is set, the number of seconds to wait until `min_count` simulators
            are running. After `timeout_seconds` has expired, the set of running simulators will be returned unless
            `raise_on_timeout` is set.
        :param raise_on_timeout: If set, will raise an exception if `timeout_seconds` has elapsed before `min_count`
            simulators have started.
        :type timeout_seconds: int
        :return: The list of currently running Simulators.
        :rtype: list(azureml.contrib.train.rl.Simulator)
        """

        start = time.time()
        while True:
            sim_count = Simulator.get_running_simulator_count()
            if timeout_seconds and time.time() - start > timeout_seconds:
                if raise_on_timeout:
                    raise Exception("Timeout has occurred waiting for {} simulators to start. "
                                    "A total of {} started before the timeout occurred.".format(min_count, sim_count))
                break
            if min_count is None or sim_count >= min_count:
                break
            else:
                print("{} simulators have started so far; waiting for {} simulators total."
                      .format(sim_count, min_count))
                time.sleep(10)

        sims = []
        for item in Simulator._get_simulator_files():
            sim = Simulator._create_from_file(item)
            if sim:
                sims.append(sim)

        return sims

    @staticmethod
    def get_simulator_by_id(simulator_id, block=True, timeout_seconds=None):
        """Get a simulator given an ID.

        By default, the method will block until the simulator is running.

        :param simulator_id: The ID of the simulator.
        :type simulator_id: str
        :param block: When set, the method will block until the simulator is running or `timeout_seconds` has elapsed.
        :type block: bool
        :param timeout_seconds: If `block` is set to True, the number of seconds to wait before failing.
        :type timeout_seconds: int
        :return: A simulator with the given ID. If the simulator doesn't start within `timeout_seconds`,
            None is returned.
        :rtype: azureml.contrib.train.rl.Simulator
        """
        path = Simulator._get_file_share_path()
        file_path = path.joinpath(Path(simulator_id + Simulator._FILE_EXTENSION))
        start = time.time()
        while block and not file_path.exists():
            print("Waiting for simulator {} to start.".format(simulator_id))
            if timeout_seconds and time.time() - start > timeout_seconds:
                break
            time.sleep(10)

        if file_path.exists():
            return Simulator._create_from_file(file_path)

    @staticmethod
    def get_running_simulator_count():
        """Get the count of currently running simulators.

        :return: The count of current running simulators.
        :rtype: int
        """

        return len([f for f in Simulator._get_simulator_files()])

    @staticmethod
    def get_simulator_count():
        """Get the number of simulators requested to run.

        :return: The number of simulators.
        :rtype: int
        """
        count = os.getenv("AZUREML_NUMBER_OF_SIMULATORS")
        if not count:
            raise Exception("The methods in the Simulator class can only be used from AmlCompute nodes.")
        elif not count.isdigit():
            raise Exception("AZUREML_NUMBER_OF_SIMULATORS should be an integer.")

        return int(count)

    @staticmethod
    def get_simulator_health_check_timeout():
        """Get the user input setting for health check frequency in seconds. The default is 15 seconds.

        :return: The time lapse between health checks in seconds.
        :rtype: int
        """
        count = os.getenv("AZUREML_SIMULATOR_HEALTH_CHECK_TIMEOUT")
        if not count:
            count = 15
            print("Unable to find user setting using default of {0} seconds.", count)
        elif not count.isdigit():
            raise Exception("AZUREML_SIMULATOR_HEALTH_CHECK_TIMEOUT should be an integer.")

        return int(count)

    @staticmethod
    def _get_file_share_path():
        path = os.getenv("AZUREML_SIMULATOR_CONTROL_PATH")
        if not path:
            raise Exception("The methods in the Simulator class can only be used from AmlCompute nodes.")

        path = os.path.expandvars(path)
        return Path(path)

    @staticmethod
    def _get_simulator_folder():
        _simulators_folder = os.environ.get("AZUREML_SIMULATOR_CONTROL_PATH")
        if not _simulators_folder:
            raise Exception("The methods in the Simulator class can only be used from AmlCompute nodes.")
        _simulators_folder = os.path.expandvars(_simulators_folder)

        # Hack to overcome bug in ES and batch some env var are not set for windows
        if os.name is 'nt':
            filestore_mount_path = os.environ.get("AZ_BATCHAI_INPUT_AZUREML").replace("/azureml", "")
            _simulators_folder = _simulators_folder.replace("__", "_", 1)
            _simulators_folder = _simulators_folder.replace("$AZ_BATCHAI_JOB_MOUNT_workspacefilestore",
                                                            filestore_mount_path)

        if not os.path.exists(_simulators_folder):
            os.makedirs(_simulators_folder, exist_ok=True)

        return _simulators_folder

    @staticmethod
    def _get_simulator_files():
        path = Simulator._get_file_share_path()
        if not path.exists():
            print("Simulator control path '{}' does not exist.".format(path))
            return

        for item in path.iterdir():
            if item.is_file() and item.suffix == Simulator._FILE_EXTENSION:
                yield item

    @staticmethod
    def _create_from_file(file):
        sim_id = file.stem
        with file.open() as f:
            address = f.readline()
            if address:
                ip_port = address.split(":")
                # remove newline in case health usage added one
                port = ip_port[1].strip()
                return Simulator(sim_id, ip_port[0], port)
            else:
                raise Exception("Invalid sim file for simulator ID: {}. IP address and port not present."
                                .format(sim_id))

    def get_health_status(self):
        """Get the latest simulator health status given an ID with a timestamp.

        :return: The HealthStatus of simulators.
        :rtype: [azureml.contrib.train.rl.Simulator.HealthStatus, time_stamp].
        """
        _filename = self._get_filename()
        enum_status = Simulator.HealthStatus.error
        file_modified_timestamp = 0

        try:
            with portalocker.Lock(_filename, "r") as f:
                file_modified_timestamp = os.path.getmtime(_filename)
                for file_line in iter(f.readline, ''):
                    if Simulator._HEALTH_CHECK_PREFIX in file_line:
                        status = file_line.split(Simulator._HEALTH_CHECK_PREFIX)[1]
                        print("Found health status {0}".format(status))
                        enum_status = Simulator.HealthStatus[status]
                        break
        except IOError as _e:
            print("No status exists. Simulator must be starting up.")
            return [Simulator.HealthStatus.starting, file_modified_timestamp]
        except Exception as _e:
            print("Get health update exception {0}".format(_e))
            raise Exception("Health Update Exception.")

        return [enum_status, file_modified_timestamp]

    def update_health_status(self, status):
        """Update Reinforcement Learning with the latest simulator health status given an ID.

        :param status: Latest health update.
        :type: azureml.contrib.train.rl.Simulator.HealthStatus.
        """
        _file_contents = "{0}:{1}\n".format(self.ip_address, self.port) + \
            "{0}{1}".format(Simulator._HEALTH_CHECK_PREFIX, status.name)

        Simulator._write_to_file(self, _file_contents)

    def _write_to_file(self, info):
        # update RL which will look for id with an updated status
        _filename = self._get_filename()

        try:
            with portalocker.Lock(_filename, "w+") as f:
                f.write(info)
                f.flush()
                os.fsync(f.fileno())
            print("Writing simulator information {0} to {1}".format(info, _filename))
        except Exception as _e:
            print("Send update exception {0}".format(_e))
            raise Exception("Update Exception.")

    def _file_exist(self):
        _filename = self._get_filename()
        return os.path.exists(_filename)

    def _clean_file(self):
        _filename = self._get_filename()
        if self._file_exist():
            print("Cleaning simulator file")
            os.remove(_filename)

    def _get_filename(self):
        _simulators_folder = self._get_simulator_folder()
        file = str(self.id) + Simulator._FILE_EXTENSION
        _filename = os.path.join(_simulators_folder, file)
        return _filename
