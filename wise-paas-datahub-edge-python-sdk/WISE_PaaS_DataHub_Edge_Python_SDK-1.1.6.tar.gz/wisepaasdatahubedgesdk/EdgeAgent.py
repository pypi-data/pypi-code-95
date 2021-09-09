import sys
import uuid
import json
import urllib.request
import threading
import paho.mqtt.client as mqtt

import wisepaasdatahubedgesdk.Common.Constants as constant
import wisepaasdatahubedgesdk.Common.Topic as mqttTopic
from wisepaasdatahubedgesdk.Model.Edge import MQTTOptions, TimeSyncCommand, ConfigAck, WriteValueCommand, Device, Tag
from wisepaasdatahubedgesdk.Model.MQTTMessage import *
import wisepaasdatahubedgesdk.Common.Converter as Converter
from wisepaasdatahubedgesdk.Model.Event import *
from wisepaasdatahubedgesdk.Common.Utils import RepeatedTimer
from wisepaasdatahubedgesdk.Common.DataRecoverHelper import DataRecoverHelper
import wisepaasdatahubedgesdk.Common.Logger as logger

class EdgeAgent():

  def __init__(self, options = None):
    self.__options = options
    self.__client = None
    self.__heartbeatInterval = constant.HeartbeatInterval
    if options and options.heartbeat:
      self.__heartbeatInterval = options.heartbeat
    self.__recoverHelper = DataRecoverHelper()
    self.__on_connected = None
    self.__on_disconnected = None
    self.__on_messageReceived = None
    # DataRecover
    # MqttTcpChannel.CustomCertificateValidationCallback = ( x509Certificate, x509Chain, sslPolicyErrors, mqttClientTcpOptions ) => { return true; };

  ## Private Method
  def __connect(self):
    try:
      if self.__options.connectType == constant.ConnectType['DCCS']:
        self.__getCredentialFromDCCS()
      
      host = self.__options.MQTT.hostName
      port = self.__options.MQTT.port
      userName = self.__options.MQTT.userName
      password = self.__options.MQTT.password
      transport = self.__options.MQTT.protocalType
      topic = mqttTopic.NodeConnTopic.format(self.__options.nodeId)

      if self.__client is None:
        clientId = 'EdgeAgent_' + str(uuid.uuid4())
        self.__client = mqtt.Client(client_id = clientId, clean_session = True, transport = transport)
        self.__client.connected_flag = False
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.on_disconnect = self.__on_disconnect

      self.__client.username_pw_set(userName, password)
      willPayload = LastWillMessage().getJson()
      self.__client.will_set(topic, payload = willPayload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = True)    
      # TLS
      self.__client.reconnect_delay_set(min_delay = self.__options.reconnectInterval, max_delay = self.__options.reconnectInterval)
    except Exception as error:
      logger.printError(e = error, msg = 'Connection setting error !')
    try:
      self.__client.loop_start()
      self.__client.connect(host, port)
    except Exception as error:
      logger.printError(e = error, msg = 'Connect error !')

  def __disconnect(self):
    if self.__options.type == constant.EdgeType['Gateway']:
      topic = mqttTopic.NodeConnTopic.format(self.__options.nodeId)
    else:
      topic = mqttTopic.DeviceConnTopic.format(self.__options.nodeId, self.__options.deviceId)
    disconnectPayload = DisconnectMessage().getJson()
    infot = self.__client.publish(topic, payload = disconnectPayload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = True)
    infot.wait_for_publish()
    self.__client.loop_stop()
    self.__client.disconnect()

  def __getCredentialFromDCCS(self):
    try:
      uri = '{0}/v1/serviceCredentials/{1}'.format(self.__options.DCCS.apiUrl, self.__options.DCCS.credentialKey)
      response = urllib.request.urlopen(uri).read().decode('utf-8').replace('"', '\"')
      response = json.loads(response)
      host = response['serviceHost']
      if self.__options.useSecure:
        port = response['credential']['protocols']['mqtt+ssl']['port']
        userName = response['credential']['protocols']['mqtt+ssl']['username']
        password = response['credential']['protocols']['mqtt+ssl']['password']
      else:
        port = response['credential']['protocols']['mqtt']['port']
        userName = response['credential']['protocols']['mqtt']['username']
        password = response['credential']['protocols']['mqtt']['password']
      mqttOptions = MQTTOptions(hostName = host, port = port, userName = userName, password = password)
      self.__options.MQTT = mqttOptions
    except Exception as error:
      logger.printError(e = error, msg = 'Get MQTT credentials from DCCS failed !')

  def __dataRecover(self):
    if not self.isConnected:
      return
    if self.__recoverHelper is None or not self.__recoverHelper.isDataExist:
      return
    payloads = self.__recoverHelper.read()
    topic = mqttTopic.DataTopic.format(self.__options.nodeId)
    for payload in payloads:
      self.__client.publish(topic, payload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = False)

  def __sendHeartbeat(self):
    if self.__client is None or not self.__client.connected_flag: 
      return
    if self.__options.type == constant.EdgeType['Gateway']:
      topic = mqttTopic.NodeConnTopic.format(self.__options.nodeId)
    else:
      topic = mqttTopic.DeviceConnTopic.format(self.__options.nodeId, self.__options.deviceId)
    heartbeatPayload = HeartbeatMessage().getJson()
    self.__client.publish(topic, payload = heartbeatPayload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = True)
    # second = self.__heartbeatInterval
    # self.__timer = threading.Timer(second, self.__sendHeartbeat)
    # self.__timer.start()
    return

  def __sendData(self, data):
    try:
      (result, payloads) = Converter.convertData(data)
      if result:
        for payload in payloads:
          if not self.isConnected():
            self.__recoverHelper.write(payload)
          else:
            topic = mqttTopic.DataTopic.format(self.__options.nodeId)
            self.__publishData(topic, payload = payload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = False)
            #self._client.publish(topic, payload = payload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = False)"""
          # self.__recoverHelper.write(payload)
          # test data recover
      return result
    except Exception as error:
      logger.printError(e = error, msg = 'Send data error !')
      return False

  def __sendDeviceStatus(self, deviceStatus):
    try:
      (result, payload) = Converter.convertDeviceStatus(deviceStatus)
      if result:
        topic = mqttTopic.NodeConnTopic.format(self.__options.nodeId)
        self.__client.publish(topic, payload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = True)
      return result
    except Exception as error:
      logger.printError(e = error, msg = 'Send device status error !')
      return False

  def __uploadConfig(self, action, edgeConfig):
    try:
      nodeId = self.__options.nodeId
      if action == constant.ActionType['Create']:
        (result, payload) = Converter.convertCreateorUpdateConfig(action = action, nodeId = nodeId, config = edgeConfig, heartbeat = self.__options.heartbeat)
      elif action == constant.ActionType['Update']:
        (result, payload) = Converter.convertCreateorUpdateConfig(action = action, nodeId = nodeId, config = edgeConfig, heartbeat = self.__options.heartbeat)
      elif action == constant.ActionType['Delete']:
        (result, payload) = Converter.convertDeleteConfig(action = action, nodeId = nodeId, config = edgeConfig)
      elif action == constant.ActionType['Delsert']:
        (result, payload) = Converter.convertCreateorUpdateConfig(action = action, nodeId = nodeId, config = edgeConfig, heartbeat = self.__options.heartbeat)
      else:
        raise ValueError('config action is invalid !') 
      topic = mqttTopic.ConfigTopic.format(self.__options.nodeId)
      self.__client.publish(topic, payload = payload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = False)
      return result
    except Exception as error:
      logger.printError(e = error, msg = 'Upload config error !')
      return False

  def __publishConfig(self, topic = None, payload = None, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = False):
    if self.__client is None or not self.__client.connected_flag:
      return
    if topic is None or payload is None:
      return
    (rc, mid) = self.__client.publish(topic, payload = payload, qos = qos, retain = retain)
    if rc == 0:
      return (True, None)
    elif rc == 1:
      return (False, 'MQTT_ERR_NO_CONN')
    elif rc == 2:
      return (False, 'MQTT_ERR_QUEUE_SIZE')

  def __publishData(self, topic = None, payload = None, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = False):
    if self.__client is None or not self.__client.connected_flag:
      return
    if topic is None or payload is None:
      return
    (rc, mid) = self.__client.publish(topic, payload = payload, qos = qos, retain = retain)
    if rc == 0:
      return (True, None)
    else:
      self.__recoverHelper.write(payload)
    if rc == 1:
      return (False, 'MQTT_ERR_NO_CONN')
    elif rc == 2:
      return (False, 'MQTT_ERR_QUEUE_SIZE')

  def __on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      self.__client.connected_flag = True
      print('Connected OK Returned code=', rc)
      # subscribe
      if self.__options.type == constant.EdgeType['Gateway']:
        cmdTopic = mqttTopic.NodeCmdTopic.format(self.__options.nodeId)
        connTopic = mqttTopic.NodeConnTopic.format(self.__options.nodeId)
      else:
        cmdTopic = mqttTopic.DeviceCmdTopic.format(self.__options.nodeId, self.__options.deviceId)
        connTopic = mqttTopic.DeviceConnTopic.format(self.__options.nodeId, self.__options.deviceId)
      ackTopic = mqttTopic.AckTopic.format(self.__options.nodeId)
      for topic in [ackTopic, cmdTopic]:
        (result, mid) = self.__client.subscribe(topic, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'])
        if result == 0:
          print('subscribe {0} successfully'.format(topic))
        else:
          print('subscribe {0} failed'.format(topic))
      # publish
      connectPayload = ConnectMessage().getJson()
      self.__client.publish(connTopic, payload = connectPayload, qos = constant.MqttQualityOfServiceLevel['AtLeastOnce'], retain = True)
      self.__sendHeartbeat()
      second = self.__heartbeatInterval
      self.__heartBeatTimer = RepeatedTimer(second, self.__sendHeartbeat)
      if self.__options.dataRecover:
        self.__dataRecoverTimer = RepeatedTimer(constant.DataRecoverInterval, self.__dataRecover)
    else:
      print('Bad connection Returned code=', rc)
      if rc == 1 or rc == 2:
        clientId = 'EdgeAgent_' + str(uuid.uuid4())
        transport = self.__options.MQTT.protocalType
        self.__client = self.__client.reinitialise(client_id = clientId, clean_session = True, transport = transport)
      if rc == 3 or rc == 4 or rc == 5:
        if self.__options.connectType == constant.ConnectType['DCCS']:
          self.__getCredentialFromDCCS()
        userName = self.__options.MQTT.userName
        password = self.__options.MQTT.password
        self.__client.username_pw_set(userName, password)
      # 1: Connection refused - incorrect protocol version
      # 2: Connection refused - invalid client identifier
      # 3: Connection refused - server unavailable
      # 4: Connection refused - bad username or password
      # 5: Connection refused - not authorised
    if self.__on_connected:
      self.__on_connected(self, isConnected = self.__client.connected_flag)

  def __on_message(self, client, userdata, msg):
    try:
      message = str(msg.payload.decode("utf-8"))
      message = json.loads(message)
      # topic = msg.topic
      if not message or not message['d']:
        return
      if 'Cmd' in message['d']:
        if not message['d']['Cmd']:
          return
        cmd = message['d']['Cmd']
        if cmd == 'WV':
          messageType = constant.MessageType['WriteValue']
          writeValueMessage = WriteValueCommand()
          if message['d']['Val']:
            for deviceId, tags in message['d']['Val'].items():
              d = Device(deviceId)
              for tagName, value in tags.items():
                d.tagList.append(Tag(tagName, value))
              writeValueMessage.deviceList.append(d)
          message = writeValueMessage
        else:
          return
      elif 'Cfg' in message['d']:
        messageType = constant.MessageType['ConfigAck']
        result = bool(message['d']['Cfg'])
        message = ConfigAck(result = result)
      else:
        return

      if self.__on_messageReceived:
        self.__on_messageReceived(self, MessageReceivedEventArgs(msgType = messageType, message = message))

    except Exception as error:
      pass
      #logger.printError(e = error, msg = 'Message received event error !')

  def __on_disconnect(self, client, userdata, rc):
    if rc == 0:
      self.__client.connected_flag = False
      self.__heartBeatTimer.stop()
      if self.__options.dataRecover:
        self.__dataRecoverTimer.stop()
    else:
      print('Bad disconnect reconnecting Returned code=', rc)
    if self.__on_disconnected:
      self.__on_disconnected(self, isDisconnected = (not self.__client.connected_flag))

  ## Public Method
  def connect(self):
    if self.__client and self.__client.connected_flag:
      return
    if self.__options is None:
      return
    self.__connect()

  def disconnect(self):
    if self.__client is None:
      return
    if self.__client and not self.__client.connected_flag:
      return
    self.__disconnect()

  def isConnected(self):
    if self.__client is None:
      return False
    else:
      return self.__client.connected_flag

  def uploadConfig(self, action = None, edgeConfig = None):
    if not self.isConnected or edgeConfig is None:
      return False
    return self.__uploadConfig(action, edgeConfig)

  def sendData(self, data = None):
    if data is None: 
      return False
    return self.__sendData(data)

  def sendDeviceStatus(self, deviceStatus = None):
    if not self.isConnected:
      return False
    if deviceStatus is None:
      return False
    return self.__sendDeviceStatus(deviceStatus)

  @property
  def on_connected(self):
    return self.__on_connected

  @on_connected.setter
  def on_connected(self, func):
    self.__on_connected = func
  
  @property
  def on_disconnected(self):
    return self.__on_disconnected

  @on_disconnected.setter
  def on_disconnected(self, func):
    self.__on_disconnected = func
  
  @property
  def on_message(self):
    return self.__on_messageReceived
  
  @on_message.setter
  def on_message(self, func):
    self.__on_messageReceived = func