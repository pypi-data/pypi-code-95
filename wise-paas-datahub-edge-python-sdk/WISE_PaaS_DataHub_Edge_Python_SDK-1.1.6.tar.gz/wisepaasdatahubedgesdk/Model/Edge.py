import datetime

import wisepaasdatahubedgesdk.Common.Constants as constant

class EdgeAgentOptions():
  def __init__(self, 
    reconnectInterval = 1, # seconds
    nodeId = 'nodeId', # None
    deviceId = 'deviceId', # None
    type = constant.EdgeType['Gateway'],
    heartbeat = constant.HeartbeatInterval,
    dataRecover = True,
    connectType = constant.ConnectType['DCCS'],
    useSecure = False,
    MQTT = None,
    DCCS = None
  ):
    self.reconnectInterval = reconnectInterval
    self.nodeId = nodeId
    self.deviceId = deviceId
    self.type = type
    self.heartbeat = heartbeat
    self.connectType = connectType
    self.useSecure = useSecure
    self.dataRecover = dataRecover
    self.MQTT = MQTT
    self.DCCS = DCCS

    if self.nodeId is None:
      raise ValueError('nodeId can not be empty')
    if self.heartbeat < 1:
      self.hearbeat = 1

class MQTTOptions():
  def __init__(self, hostName = None, port = 1883, userName = None, password = None, protocalType = constant.Protocol['TCP']):
    self.hostName = hostName
    self.port = int(port)
    self.userName = userName
    self.password = password
    self.protocalType = protocalType
    if hostName == '' or hostName is None:
      raise ValueError('hostName can not be empty')
    # if not port.isdigit():
    #   raise ValueError('port must be Number')
    if userName == '' or userName is None:
      raise ValueError('userName can not be empty')
    if password == '' or password is None:
      raise ValueError('password can not be empty')
    if not protocalType in constant.Protocol.values():
      raise ValueError('protocalType is not exist.')

class DCCSOptions():
  def __init__(self, apiUrl = None, credentialKey = None):
    if apiUrl[-1] == '/':
      apiUrl = apiUrl[:-1]
    self.apiUrl = apiUrl
    self.credentialKey = credentialKey
    if apiUrl == '' or apiUrl is None:
      raise ValueError('apiUrl can not be empty')
    if credentialKey == '' or credentialKey is None:
      raise ValueError('credentialKey can not be empty')

class EdgeData():
  def __init__(self):
    self.tagList = []
    self.timestamp = datetime.datetime.utcnow()

class EdgeTag():
  def __init__(self, deviceId = None, tagName = None, value = object()):
    self.deviceId = deviceId
    self.tagName = tagName
    self.value = value

class EdgeStatus():
  def __init__(self, id = None, status = constant.Status['Offline']):
    self.id = id
    self.status = status

class EdgeDeviceStatus():
  def __init__(self):
    self.deviceList = []

class EdgeConfig():
  def __init__(self):
    self.node = NodeConfig()

class NodeConfig():
  def __init__(self, nodeType = constant.EdgeType['Gateway']):
    self.type = nodeType
    self.deviceList = []
  
  def isValid(self):
    if self.type is None:
      return (False, ValueError('nodeType is necessary'))
    if not (self.type in constant.EdgeType.values()):
      return (False, ValueError('nodeType is invalid'))
    return (True, None)

class DeviceConfig():
  def __init__(self, id = None, name = None, comPortNumber = None, deviceType = None, description = None, ip = None, port = None, retentionPolicyName = None):
    self.id = id
    self.name = name
    self.comPortNumber = comPortNumber
    self.type = deviceType
    self.description = description
    self.ip = ip
    self.port = port
    self.retentionPolicyName = retentionPolicyName
    self.analogTagList = []
    self.discreteTagList = []
    self.textTagList = []
    if self.id is None or self.id == '':
      raise ValueError('id is necessary')

  def isValid(self):
    if self.name is None:
      return (False, ValueError('name is necessary'))
    if self.type is None:
      return (False, ValueError('deviceType is necessary'))
    return (True, None)

class TagConfig():
  def __init__(self, name = None, description = None, readOnly = None, arraySize = None):
    self.name = name
    self.description = description
    self.readOnly = readOnly
    self.arraySize = arraySize
    if self.name is None or self.name == '':
      raise ValueError('name is necessary')

class AnalogTagConfig(TagConfig):
  def __init__(self, name = None, description = None, readOnly = None, arraySize = None, spanHigh = None, spanLow = None, engineerUnit = None, integerDisplayFormat = None, fractionDisplayFormat = None):
    super(AnalogTagConfig, self).__init__(name = name, description = description, readOnly = readOnly, arraySize = arraySize)
    self.spanHigh = spanHigh
    self.spanLow = spanLow
    self.engineerUnit = engineerUnit
    self.integerDisplayFormat = integerDisplayFormat
    self.fractionDisplayFormat = fractionDisplayFormat

class DiscreteTagConfig(TagConfig):
  def __init__(self, name = None, description = None, readOnly = None, arraySize = None, state0 = None, state1 = None, state2 = None, state3 = None, state4 = None, state5 = None, state6 = None, state7 = None):
    super(DiscreteTagConfig, self).__init__(name = name, description = description, readOnly = readOnly, arraySize = arraySize)
    self.state0 = state0
    self.state1 = state1
    self.state2 = state2
    self.state3 = state3
    self.state4 = state4
    self.state5 = state5
    self.state6 = state6
    self.state7 = state7

class TextTagConfig(TagConfig):
  def __init__(self, name = None, description = None, readOnly = None, arraySize = None):
    super(TextTagConfig, self).__init__(name = name, description = description, readOnly = readOnly, arraySize = arraySize)

class TimeSyncCommand():
  def __init__(self, time = datetime.datetime.utcnow()):
    self.UTCTime = time

class ConfigAck():
  def __init__(self, result = False):
    self.result = result

class WriteValueCommand():
  def __init__(self):
    self.deviceList = []

class Device():
  def __init__(self, id = None):
    self.id = id
    self.tagList = []

class Tag():
  def __init__(self, name = None, value = None):
    self.name = name
    self.value = value