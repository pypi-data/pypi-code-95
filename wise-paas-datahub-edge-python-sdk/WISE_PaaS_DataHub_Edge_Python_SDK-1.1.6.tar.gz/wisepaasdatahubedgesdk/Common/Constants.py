HeartbeatInterval = 60  #second
DataRecoverInterval = 3 #second
DefaultReadRecordCount = 10
DefaultWriteRecoredCount = 1000
DBFileName = 'recover.sqlite'

DataMaxTagCount = 100

ActionType = {
  'Create': 1,
  'Update': 2,
  'Delete': 3,
  'Delsert': 4
}
ConnectType = {
  'MQTT': 'MQTT',
  'DCCS': 'DCCS'
}
Protocol = {
  'TCP': 'tcp',
  'WebSocket': 'websockets'
}
MqttQualityOfServiceLevel = {
  'AtMostOnce': 0,
  'AtLeastOnce': 1,
  'ExactlyOnce': 2
}
EdgeType = {
  'Gateway': 0,
  'Device': 1
}
TagType = {
  'Analog': 1,
  'Discrete': 2,
  'Text': 3
}
MessageType = {
  'WriteValue': 0,
  'WriteConfig': 1,
  'TimeSync': 2,
  'ConfigAck': 3
}
Status = {
  'Offline': 0,
  'Online': 1
}
NodeConfigMapper = {
  'type': 'Type',
  'heartbeat': 'Hbt'
}
DeviceConfigMapper = {
  'name': 'Name',
  'comPortNumber': 'PNbr',
  'type': 'Type',
  'description': 'Desc',
  'ip': 'IP',
  'port': 'Port',
  'retentionPolicyName': 'RP'
}
TagConfigMapper = {
  'type': 'Type',
  'description': 'Desc',
  'readOnly': 'RO',
  'arraySize': 'Ary',
  'spanHigh': 'SH',
  'spanLow': 'SL',
  'engineerUnit': 'EU',
  'integerDisplayFormat': 'IDF',
  'fractionDisplayFormat': 'FDF',
  'state0': 'S0',
  'state1': 'S1',
  'state2': 'S2',
  'state3': 'S3',
  'state4': 'S4',
  'state5': 'S5',
  'state6': 'S6',
  'state7': 'S7'
}