# Copyright 2021 IoTFlows Inc. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable laconsole.w or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time, threading
import ssl, json
import paho.mqtt.client as paho 
import requests
from base64 import b64encode
import re

class IoTFlows:
   # Class initialization
   def __init__(self, username, password):
      self.username = username
      self.password = password
      self.connected = False
      self.client = paho.Client() 
      self.client.on_message = self.on_message
      self.client.on_log = self.on_log
      self.client.on_connect = self.on_connect      
      self.client.on_disconnect = self.on_disconnect      
      self.subscriptions = {}
      # Setting the username password
      self.client.username_pw_set(username=self.username, password=self.password)

      # Connecting to the broker  
      self.client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS)
      self.client.connect("mqtts.connect.iotflows.com", 443, 60)
      self.client.loop_start() # keep the client in a separate thread
      # self.client.loop_forever()

   # ----------------------------------------------------------------------  Callback Functions
   def on_connect(self, client, userdata, flags, rc):   
      if rc == 0:
         self.connected = True      
         print("Connected to the cloud.")
      else:
         print("Couldn't connect to the server. This can be due to the internet connection, wrong credentials, or insufficient permissions.")

   def on_disconnect(self, client, userdata, flags, rc):                
      self.connected = False      
      print("Disconnected from the cloud.")
   
   def on_log(client, userdata, level, buf):
      a = 1

   def on_message(self, client, userdata, message):  
      topic       = str(message.topic)
      payload     = str(message.payload.decode("utf-8"))
      print()
      print('MQTT new message received.')
      print('Topic: ' + topic)
      print('Payload: ' + payload)  
      payloadJson = json.loads(payload)  

   # ----------------------------------------------------------------------  API Functions
   # Publish Data Stream
   def publish(self, data_stream_uuid, data):            
      # find the index of this data_stream in topics               
      hasThisTopic = False
      i = 0
      for info in self.data_streams:           
         if(info['data_stream_uuid'] == data_stream_uuid):            
            hasThisTopic = True
            break         
         i += 1
      
      if hasThisTopic:
         # create the topic
         topic = f'''v1/organizations/{self.data_streams[i]["organization_uuid"]}/projects/{self.data_streams[i]["project_uuid"]}/devices/{self.data_streams[i]["device_uuid"]}/data-streams/{self.data_streams[i]["data_stream_uuid"]}'''         
         # create the json payload
         payload = json.dumps({"data": data, "data_stream_id": data_stream_uuid, "client_id": self.username})         
         # publish
         self.client.publish(topic, payload)    
      else:
         print('Error: data stream not found.')
   # --------------------------------------------------------

   # Publish Alert
   def alert(self, alert_channel_uuid, severity_level, subject, description):            
      # Publishes an alert to an alert channel.
      hasThisTopic = False
      i = 0
      for info in self.alert_channels:           
         if(info['alert_channel_uuid'] == alert_channel_uuid):            
            hasThisTopic = True
            break         
         i += 1
      
      if hasThisTopic:
         # create the topic
         topic = f'''v1/organizations/{self.alert_channels[i]["organization_uuid"]}/alert-channels/{self.alert_channels[i]["alert_channel_uuid"]}'''         
         # create the json payload
         payload = json.dumps({"severity_level": severity_level, "subject": subject, "description": description, "alert_channel_id": alert_channel_uuid ,"client_id": self.username})         
         # publish
         self.client.publish(topic, payload)    
      else:
         print('Error: alert channel not found.')
   # --------------------------------------------------------

   # Subscribe to Data Stream
   def subscribe(self, data_stream_uuid, qos, callback):       
      '''Subscribes to a data stream.'''
      # find the index of this data_stream in topics                     
      hasThisTopic = False
      i = 0
      for info in self.data_streams:           
         if(info['data_stream_uuid'] == data_stream_uuid):            
            hasThisTopic = True
            break         
         i += 1
      
      if hasThisTopic:
         # create the topic
         topic = f'''v1/organizations/{self.data_streams[i]["organization_uuid"]}/projects/{self.data_streams[i]["project_uuid"]}/devices/{self.data_streams[i]["device_uuid"]}/data-streams/{self.data_streams[i]["data_stream_uuid"]}'''                  
         print(topic)
         def callbackFunction(client, userdata, message):   
            mTopic = str(message.topic)               
            if str(topic) == mTopic: # TODO: make this work with wildcards
               mPayload = json.loads(str(message.payload.decode("utf-8")))["data"]                           
               callback(topic = mTopic, payload = mPayload) 

         # subscribe
         sub = { "topic": topic, "qos": qos, "handler": callbackFunction}                
         self.subscriptions[topic] = sub;             
         self.client.on_message = sub["handler"]
         self.client.subscribe(topic, qos=qos)
      else:
         print('Error: data stream not found.')
   # --------------------------------------------------------
   # Define Action
   def defineAction(self, action_uuid, qos, callback):       
      '''Defines a cloud action.'''
      # find the index of this action in topics                     
      hasThisTopic = False
      i = 0
      for info in self.actions:           
         if(info['action_uuid'] == action_uuid):            
            hasThisTopic = True
            break         
         i += 1
      
      if hasThisTopic:
         # create the topic
         topic = f'''v1/organizations/{self.actions[i]["organization_uuid"]}/projects/{self.actions[i]["project_uuid"]}/devices/{self.actions[i]["device_uuid"]}/actions/{self.actions[i]["action_uuid"]}'''                  
         print(topic)
         def callbackFunction(client, userdata, message):   
            mTopic = str(message.topic)               
            if str(topic) == mTopic: # TODO: make this work with wildcards
               mPayload = json.loads(str(message.payload.decode("utf-8")))["data"]                           
               callback(topic = mTopic, payload = mPayload) 

               # send a delivery confirmation response
               iotflows_payload = {
                  "client_id": self.username,           
                  "msg_id": json.loads(mPayload)["msg_id"],
                  "action_id": action_uuid
               }
               topicConfirmation = topic.replace('/actions/', '/actions-confirmation/');       
               print(topicConfirmation)
               print(json.loads(iotflows_payload))     
               self.client.publish(topicConfirmation, json.loads(iotflows_payload))

         # subscribe
         sub = { "topic": topic, "qos": qos, "handler": callbackFunction}
         self.subscriptions[topic] = sub;             
         self.client.on_message = sub["handler"]
         print("SUBSCRIBING...")
         self.client.subscribe(topic, qos=qos)
         print(topic)
      else:
         print('Error: data stream not found.')
   # --------------------------------------------------------

   # Call Action
   def callAction(self, action_uuid, data):            
      ''' Executes an action with a commmand '''
      # find the index of this action in topics               
      hasThisTopic = False
      i = 0
      for info in self.actions:           
         if(info['action_uuid'] == action_uuid):            
            hasThisTopic = True
            break         
         i += 1
      
      if hasThisTopic:
         # create the topic
         topic = f'''v1/organizations/{self.actions[i]["organization_uuid"]}/projects/{self.actions[i]["project_uuid"]}/devices/{self.actions[i]["device_uuid"]}/actions/{self.actions[i]["action_uuid"]}'''         
         # create the json payload
         payload = json.dumps({"data": data, "action_id": action_uuid, "client_id": self.username})         
         # publish
         self.client.publish(topic, payload)    
      else:
         print('Error: action not found.')
   # --------------------------------------------------------

def init(username, password):  
   
   # create an IoTFlows instance    
   iotflows = IoTFlows(username, password)    
      
   # Hold on until it gets connected 
   attempts = 0
   while(iotflows.connected == False): 
      time.sleep(1)          
      attempts += 1
      if(attempts > 3):
         print('Closing the application.')
         break

   if iotflows.connected:
      
      # create the auth header
      authHeader = b64encode(bytes(username + ':' + password, "utf-8")).decode("ascii")         
      
      # retrieve data stream topics
      x = requests.get(
         'https://api.iotflows.com/v1/device_clients/' + username + '/project_data_streams', 
         headers={'Authorization': 'Basic ' + authHeader})      
      iotflows.data_streams = json.loads(x.text)

      # retrieve alert channel topics
      x = requests.get(
         'https://api.iotflows.com/v1/device_clients/' + username + '/organization_alert_channels',
         headers={'Authorization': 'Basic ' + authHeader})
      iotflows.alert_channels = json.loads(x.text)

      # retrieve action topics
      x = requests.get(
         'https://api.iotflows.com/v1/device_clients/' + username + '/project_actions',
         headers={'Authorization': 'Basic ' + authHeader})
      iotflows.actions = json.loads(x.text)               
   return iotflows

