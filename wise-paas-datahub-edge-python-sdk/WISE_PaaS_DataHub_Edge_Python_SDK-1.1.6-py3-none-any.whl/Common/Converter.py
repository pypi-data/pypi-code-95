from wisepaasdatahubedgesdk.Model.MQTTMessage import *
from wisepaasdatahubedgesdk.Model.Edge import *
import wisepaasdatahubedgesdk.Common.Constants as constant
import wisepaasdatahubedgesdk.Common.Logger as logger

def convertData(data = None):
  try:
    if data is None:
      return (False, None)
    payloads = []
    dataMessage = DataMessage()
    dataMessage.setTimestamp(data.timestamp)
    tagList = data.tagList
    tagList = sorted(tagList, key = lambda tag: tag.deviceId)
    for tag in tagList:
      dataMessage.setTagValue(tag.deviceId, tag.tagName, tag.value)
    payloads.append(dataMessage.getJson())
    return (True, payloads)
  except Exception as error:
    logger.printError(e = error, msg = 'Conevert data payload failed !')
    return (False, None)
    

def convertDeviceStatus(status = None):
  try:
    if not status:
      return (False, None)
    deviceList = status.deviceList
    payload = DeviceStatusMessage()
    for device in deviceList:
      payload.setDeviceStatus(device.id, device.status)
    return (True, payload.getJson())
  except Exception as error:
    logger.printError(e = error, msg = 'Conevert device status payload failed !')
    return (False, None)

def convertCreateorUpdateConfig(action = None, nodeId = None, config = None, heartbeat = constant.HeartbeatInterval):
  try:
    if not config or not nodeId:
      return (False, None)
    payload = ConfigMessage(action, nodeId)

    node = config.node
    if not type(node) is NodeConfig:
      raise ValueError('config.node type is invalid')
    node.heartbeat = heartbeat
    (result, error) = node.isValid()
    if action == constant.ActionType['Create'] and not result:
      raise error
    payload.addNodeConfig(nodeId, node)
    for device in node.deviceList:
      if not type(device) is DeviceConfig:
        raise ValueError('config.node.device type is invalid')
      (result, error) = device.isValid()
      payload.addDeviceConfig(nodeId, deviceId = device.id, config = device)
      for tag in device.analogTagList:
        tag.type = constant.TagType['Analog']
        payload.addTagConfig(nodeId, deviceId = device.id, tagName = tag.name, config = tag)
      for tag in device.discreteTagList:
        tag.type = constant.TagType['Discrete']
        payload.addTagConfig(nodeId, deviceId = device.id, tagName = tag.name, config = tag)
      for tag in device.textTagList:
        tag.type = constant.TagType['Text']
        payload.addTagConfig(nodeId, deviceId = device.id, tagName = tag.name, config = tag)
    return (True, payload.getJson())
  except Exception as error:
    logger.printError(e = error, msg = 'Conevert config payload failed !')
    return (False, None)

def convertDeleteConfig(action = None, nodeId = None, config = None):
  try:
    if not (config or nodeId):
      return (False, None)
    payload = ConfigMessage(action, nodeId)

    node = config.node
    if not type(node) is NodeConfig:
      raise ValueError('config.node type is invalid')
    payload.deleteNodeConfig(nodeId)
    for device in node.deviceList:
      payload.deleteDeviceConfig(nodeId, deviceId = device.id)
      for listName in ['analogTagList', 'discreteTagList', 'textTagList']:
        for tag in getattr(device, listName):
          payload.deleteDeviceConfig(nodeId, deviceId = device.id)
        for tag in device.analogTagList:
          payload.deleteTagConfig(nodeId, deviceId = device.id, tagName = tag.name)
        for tag in device.discreteTagList:
          payload.deleteTagConfig(nodeId, deviceId = device.id, tagName = tag.name)
        for tag in device.textTagList:
          payload.deleteTagConfig(nodeId, deviceId = device.id, tagName = tag.name)
    return (True, payload.getJson())
  except Exception as error:
    logger.printError(e = error, msg = 'Conevert config payload failed !')
    return (False, None)
