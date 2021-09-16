import sys
import time
from IPython import embed
import threading
import logging

from samyplugin.CRCL_DataTypes import *

from opcua.common.xmlexporter import XmlExporter
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class
from opcua import Client
from opcua import ua

from pubsub import pub
from pubsub.utils import useNotifyByWriteFile
import inspect
import collections
from pprint import pprint

# Interface python3 main.py -IP SAMYCore- -Plugin Port- -IP Robot- -PluginName-

class ErrorHandler(pub.IListenerExcHandler):
    def __call__(self, listenerID, topicObj):
        print(topicObj)
        pub.sendMessage("command_error")

class Plugin():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(logging.Formatter("%(levelname)s %(filename)s - %(message)s"))
        self.logger.addHandler(log_handler)

        self.idx = None
        self.robot_node = None
        self.thread = None
        self.opcua_core_client = None
        self.next_skill_node_id = None
        self.my_skill_node = None
        self.start_method_id = None # ToDo create a dict
        self.resume_method_id = None
        self.suspend_method_id = None
        self.halt_method_id = None
        self.reset_method_id = None
        self.log_file = open("message_log.txt", "w")
        self.crcl_command_dict = None
        pub.setListenerExcHandler(ErrorHandler())
        self.log_all_messages()
        self.create_subscribers()
        #self.get_list_of_datatypes()


######################### OPCUA CLIENT SECTION #################################

    def datachange_notification(self, node, val, data):
        #print("Python: New data change event:", node, val)
        # Start a thread for each skill that gets executed
        # Get node of the skill
        self.logger.info("\n\n Subscription Info \n")
        self.logger.info(data.monitored_item.Value.SourceTimestamp)
        self.logger.info(data.monitored_item.Value.ServerTimestamp)
        self.logger.info(data.monitored_item.Value.Value)
        self.logger.info(data.monitored_item.Value.StatusCode)

        self.my_skill_node = self.opcua_core_client.get_node(val)
        self.thread = threading.Thread(target=self.command_thread, args=())
        self.thread.start()

    def event_notification(self, event):
        self.logger.info("Python: New event", event)

######################### OPCUA CLIENT SECTION END #############################

    def sort_by_number(self, elem):
        try:
            return int(elem[0][:2])
        except:
            return int(elem[0][:1])

    def command_thread(self):
        self.logger.info("Command Thread started\n")
        # Get the node id for each method of the skill
        my_skill_method_node_ids = self.my_skill_node.get_methods()
        self.logger.info(my_skill_method_node_ids)
        # Connect methodes of skill to the signals of the plugin
        for i, node_id in enumerate(my_skill_method_node_ids):
            browse_name = node_id.get_browse_name()
            self.logger.info(browse_name)
            if browse_name.Name == "Halt":
                self.halt_method_id = node_id
            elif browse_name.Name == "Reset":
                self.reset_method_id = node_id
            elif browse_name.Name == "Start":
                self.start_method_id = node_id
            elif browse_name.Name == "Resume":
                self.resume_method_id = node_id
            elif browse_name.Name == "Suspend":
                self.suspend_method_id = node_id

        parameter_set_node = self.my_skill_node.get_child("3:ParameterSet")
        parameter_set_variable_node_ids = parameter_set_node.get_variables()
        parameter_nodes = {}

        for parameter_node_id in parameter_set_variable_node_ids:
            parameter_node = self.opcua_core_client.get_node(parameter_node_id)
            parameter_nodes[parameter_node.get_browse_name().Name] = parameter_node

        parameter_nodes_sorted = sorted(parameter_nodes.items(), key=self.sort_by_number)
        #pprint(parameter_nodes_sorted)

        for i in range(len(parameter_nodes_sorted)):
            val = parameter_nodes_sorted[i][1].get_value()
            topic = self.crcl_command_dict[type(val)]
            self.logger.info(topic)
            pub.sendMessage(topic, data=val)
        pub.sendMessage("command_reset")

    def connect_to_core(self, address_, port_):
        # Connect to SAMYCore opcua server
        while True:
            try:
                # Create opcua client connection with SAMYCore
                self.logger.info("Connecting to SAMYCore")
                address = ("opc.tcp://{}:{}").format(address_, port_)
                self.opcua_core_client = Client(address)
                self.opcua_core_client.connect()
                self.logger.info("Connected to SAMYCore")
                break
            except:
                self.logger.info("Connection with SAMYCore failed!!!!!\n Retry in 3 seconds....")
                time.sleep(3)
        # Get information about all nodes of SAMYCore opcua server
        self.opcua_core_client.load_type_definitions()
        self.crcl_command_dict = {
            ua.InitCanonParametersSetDataType: "InitCanon",
            ua.EndCanonParametersSetDataType: "EndCanon",
            ua.MessageParametersSetDataType: "Message",
            ua.MoveToParametersSetDataType: "MoveTo",
            ua.MoveScrewParametersSetDataType: "MoveScrew",
            ua.MoveThroughToParametersSetDataType: "MoveThroughTo",
            ua.DwellParametersSetDataType: "Dwell",
            ua.ActuateJointsParametersSetDataType: "ActuateJoints",
            ua.ConfigureJointReportsParametersSetDataType: "ConfigureJointReports",
            #ua.ConfigureJointReportParametersSetDataType: "ConfigureJointReport",
            ua.SetDefaultJointPositionsTolerancesParametersSetDataType: "SetDefaultJointPositionsTolerances",
            ua.GetStatusParametersSetDataType: "GetStatus",
            ua.CloseToolChangerParametersSetDataType: "CloseToolChanger",
            ua.OpenToolChangerParametersSetDataType: "OpenToolChanger",
            ua.SetRobotParametersParametersSetDataType: "SetRobotParameters",
            ua.SetEndeffectorParametersParametersSetDataType: "SetEndeffectorParameters",
            ua.SetEndeffectorParametersSetDataType: "SetEndeffector",
            ua.SetTransAccelParametersSetDataType: "SetTransAccel",
            ua.SetTransSpeedParametersSetDataType: "SetTransSpeed",
            ua.SetRotAccelParametersSetDataType: "SetRotAccel",
            ua.SetRotSpeedParametersSetDataType: "SetRotSpeed",
            ua.SetAngleUnitsParametersSetDataType: "SetAngleUnits",
            ua.SetEndPoseToleranceParametersSetDataType: "SetEndPoseTolerance",
            ua.SetForceUnitsParametersSetDataType: "SetForceUnits",
            ua.SetIntermediatePoseToleranceParametersSetDataType: "SetIntermediatePoseTolerance",
            ua.SetLengthUnitsParametersSetDataType: "SetLengthUnits",
            ua.SetMotionCoordinationParametersSetDataType: "SetMotionCoordination",
            ua.SetTorqueUnitsParametersSetDataType: "SetTorqueUnits",
            ua.StopMotionParametersSetDataType: "StopMotion",
            ua.ConfigureStatusReportParametersSetDataType: "ConfigureStatusReport",
            ua.EnableSensorParametersSetDataType: "EnableSensor",
            ua.DisableSensorParametersSetDataType: "DisableSensor",
            ua.EnableGripperParametersSetDataType: "EnableGripper",
            ua.DisableGripperParametersSetDataType: "DisableGripper",
            ua.EnableRobotParameterStatusParametersSetDataType: "EnableRobotParameterStatus",
            ua.DisableRobotParameterStatusParametersSetDataType: "DisableRobotParameterStatus"
        }

    def disconnect_core(self):
        self.logger.info("Stopping plugin")
        self.opcua_core_client.disconnect()

    def subscribe_to_core(self, robot_name_):
        try:
            # Getting the root node is not stricly neccessary but recomended
            root = self.opcua_core_client.get_root_node()
            objects = self.opcua_core_client.get_objects_node()
            nodes = objects.get_child(["3:DeviceSet"])
            for object in nodes.get_children():
                if object.get_browse_name().Name == robot_name_:
                    ns = object.nodeid.NamespaceIndex
                    next_skill_node_id_node = object.get_child(["4:Controllers", "{}:{}".format(ns, robot_name_), "{}:NextSkillNodeId".format(ns)])
            # Subscribe to next_skill_node_id_node
            sub = self.opcua_core_client.create_subscription(500, self)
            handle = sub.subscribe_data_change(next_skill_node_id_node)
            embed()
        finally:
            self.logger.info("Subscription closed")
            #self.opcua_core_client.disconnect()


    def send_command_reset(self):
        self.logger.info("Command is finished")
        self.logger.info(self.reset_method_id)
        # Call methode finished in oocua server
        self.my_skill_node.call_method(self.reset_method_id)

    def send_command_halt(self):
        self.logger.info("Command is on hold")
        self.logger.info(self.halt_method_id)
        # Call methode halt in opcua server
        self.my_skill_node.call_method(self.halt_method_id)

    def send_command_error(self):
        self.logger.error("Command faild to execute")
        self.logger.error("Error:", exc_info=True)
        # Call methode error in opcua
        #self.my_skill_node.call_method(self.)

    def send_command_suspend(self):
        self.logger.info("Command suspended")
        self.logger.info(self.suspend_method_id)
        # Call methode error in opcua
        self.my_skill_node.call_method(self.suspend_method_id)

    def log_all_messages(self):
        useNotifyByWriteFile(self.log_file)

    def create_subscribers(self):
        pub.subscribe(self.send_command_reset, "command_reset")
        pub.subscribe(self.send_command_halt, "command_halt")
        pub.subscribe(self.send_command_error, "command_error")
        pub.subscribe(self.send_command_suspend, "command_suspend")
