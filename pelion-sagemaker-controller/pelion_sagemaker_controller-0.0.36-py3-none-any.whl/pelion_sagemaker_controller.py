# pelion_sage_controller_api.py

# Sagemaker Imports
import sagemaker
from sagemaker import get_execution_role
import boto3
import tensorflow as tf
import numpy as np

# Requirements
import os
import base64
import time
import tarfile
import json
import requests
import uuid

# TF Helpers
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from IPython.display import display

#
# AWS Sagemaker Edge Agent via Pelion controller API
#
class ControllerAPI:
    # Constructor
    def __init__(self, api_key, pt_device_id, api_endpoint='api.us-east-1.mbedcloud.com',async_response_sec=0.25):
        # To Do: Lets keep the API Key as protected as possible... 
        self.pelion_api_key = api_key

        # We could make the Pelion Edge Sagemaker Edge Agent PT Device ID variable as well...
        self.pelion_pt_device_id = pt_device_id
        
        # Tunable to wait between long polling...in seconds
        self.async_response_wait_time_sec = async_response_sec
        
        # Tunable to determine how long to wait for a result before declaring timeout
        self.max_result_waittime = 20 # seconds
        self.max_iteration_check = int(self.max_result_waittime / async_response_sec)
        
        # How many times to try POST to Pelion
        self.max_num_post_tries = 2 # 2 tries...
        
        # Pelion Edge Sagemaker Edge Agent Device surfaces out these three LWM2M resources
        self.pelion_rpc_request_lwmwm_uri = '/33311/0/5701'  # JsonRPC command resource
        self.pelion_config_lwm2m_uri      = '/33311/0/5702'  # Config set/get resource
        self.pelion_cmd_status_lwm2m_uri  = '/33311/0/5703'  # Long-running command completion status resource

        # Standard Pelion Northbound API plumbing with our selected device ID from above...
        self.pelion_api_endpoint = api_endpoint
        self.pelion_request_headers = {'Authorization':'Bearer ' + self.pelion_api_key, 'content-type':'application/json' }
        self.pelion_long_poll_url = 'https://' + self.pelion_api_endpoint + '/v2/notification/pull'
        self.pelion_device_requests_url = 'https://' + self.pelion_api_endpoint + '/v2/device-requests/' + self.pelion_pt_device_id + '?async-id='
        self.pelion_ping_url = 'https://' + self.pelion_api_endpoint + '/v2/endpoints/' + self.pelion_pt_device_id 

    # Pelion DeviceRequests Dispatch (internal)
    def __pelion_device_request_dispatch(self, req_id, verb, uri, json_data):
        # We need to "wake up" Pelion so issue a "get"...
        # print('PelionSageAgent (PING): ' + self.pelion_ping_url)
        requests.get(self.pelion_ping_url, headers=self.pelion_request_headers)
        
        # process the input payload
        pelion_b64_payload = ''
        if json_data != '':
            pelion_b64_payload = base64.b64encode(json.dumps(json_data).encode('utf-8')).decode('utf-8')

        # Pelion Dispatch Command
        pelion_device_requests_cmd = { "method": verb, "uri": uri }
        if pelion_b64_payload != '':
            pelion_device_requests_cmd["payload-b64"] = pelion_b64_payload

        # Make the call to invoke the command...
        dispatch_url = self.pelion_device_requests_url + req_id
        
        # Try this a few times if needed
        for post_try in range(0, self.max_num_post_tries):
            pelion_cmd_response = requests.post(dispatch_url, data=json.dumps(pelion_device_requests_cmd), headers=self.pelion_request_headers)
            print('PelionSageAPI (' + verb + ')[' + str(post_try) + ']: Url: ' + dispatch_url + " Data: " + str(pelion_device_requests_cmd) + " Status: " + str(pelion_cmd_response.status_code))

            # Now Long Poll to get the command dispatch response..
            iteration_check = 1
            pelion_command_response = {}
            iteration_status = 0
            DoPoll = True
            if pelion_cmd_response.status_code >= 200 and pelion_cmd_response.status_code < 300:
                # Command succeeded - look for the result...
                while DoPoll:
                    long_poll_responses = requests.get(self.pelion_long_poll_url, headers=self.pelion_request_headers)
                    responses_json = json.loads(long_poll_responses.text)
                    if 'async-responses' in responses_json:
                        for response in responses_json['async-responses']:
                            if response['id'] == req_id:
                                pelion_command_response = {}
                                pelion_command_response['status_code'] = 200 #default is OK... we refine below...
                                if 'status' in response:
                                    pelion_command_response['status_code'] = response['status']
                                if 'payload' in response:
                                    if response['payload'] != '':
                                        pelion_command_response = json.loads(base64.b64decode(response['payload']))
                                        if 'status' in response:
                                            pelion_command_response['status_code'] = response['status']
                                DoPoll = False
                                iteration_status = 1
                    if DoPoll == True:
                        time.sleep(self.async_response_wait_time_sec)
                        iteration_check = iteration_check + 1
                        if iteration_check > self.max_iteration_check:
                            print('PelionSageAPI (' + verb + '): Timeout reached looking for result')
                            pelion_command_response['status_code'] = 408
                            pelion_command_response['url'] = dispatch_url
                            pelion_command_response['verb'] = verb
                            DoPoll = False
                            iteration_status = 3
            else:
                # Command failed - report the status...
                print('PelionSageAPI (' + verb + '): FAILED with status: ' + str(pelion_cmd_response.status_code))
                pelion_command_response['status_code'] = pelion_cmd_response.status_code
                pelion_command_response['url'] = dispatch_url
                pelion_command_response['verb'] = verb
                iteration_status = 2
                
            if iteration_status == 1:
                # Success - so just return
                return pelion_command_response
            if iteration_status == 3 and post_try >= (self.max_num_post_tries-1):
                # Timeout and max number of post tries about to be exceeded
                return pelion_command_response
            if iteration_status == 2:
                # Error from Pelion - so just return with the error
                return pelion_command_response
        
    # Pelion LWM2M Value Request (internal)
    def __pelion_get(self,req_id, uri):
        return self.__pelion_device_request_dispatch(req_id, 'GET', uri, '')

    # Pelion LWM2M POST Execute (internal)
    def __pelion_post(self,req_id, uri, json_data):
        return self.__pelion_device_request_dispatch(req_id, 'POST', uri, json_data)

    # Pelion LWM2M PUT Operation (internal)
    def __pelion_put(self,req_id, uri, json_data):
        return self.__pelion_device_request_dispatch(req_id, 'PUT', uri, json_data)

    # Get the last value of our LWM2M RPC Interface
    def pelion_last_cmd_result(self):
        req_id = str(uuid.uuid4())
        return self.__pelion_get(req_id,self.pelion_rpc_request_lwmwm_uri)

    #
    # Configuration API
    #
    
    # Get Configuration
    def pelion_get_config(self, key=None):
        req_id = str(uuid.uuid4())
        my_config = self.__pelion_get(req_id,self.pelion_config_lwm2m_uri)
        if key == None:
            return my_config
        else:
            return my_config['config'][key]

    # Set Configuration
    def pelion_set_config(self,key,value):
        req_id = str(uuid.uuid4())
        config_update = {"jsonrpc":"2.0","id":req_id,"config":{}}
        config_update['config'][key] = value
        result = self.__pelion_put(req_id,self.pelion_config_lwm2m_uri,config_update)
        if result['status_code'] >= 200 and result['status_code'] < 300:
            return self.pelion_get_config()
        else:
            print("PelionSageAPI (PUT) set_config FAILED with status: " + str(result['status_code']))
            return result

    #
    # Sagemaker Controls
    # These commands need to conform to the JsonRPC format presented in SageMakerEdgeAgentContainer/sagemaker-agent-pt.js
    #
    
    # Is dispatched command running?
    def pelion_cmd_is_running(self,command):
        req_id = str(uuid.uuid4())
        status = self.__pelion_get(req_id,self.pelion_cmd_status_lwm2m_uri)
        if command in status:
            if status[command] == 'running':
                return True
        return False
    
    # Is dispatch command in error?
    def pelion_cmd_in_error(self,command):
        req_id = str(uuid.uuid4())
        status = self.__pelion_get(req_id,self.pelion_cmd_status_lwm2m_uri)
        if command in status:
            if status[command] == 'error':
                return True
        return False
    
    # ListModels
    def pelion_list_models(self):
        req_id = str(uuid.uuid4())
        result = self.__pelion_post(req_id, self.pelion_rpc_request_lwmwm_uri, {"jsonrpc":"2.0","id":req_id,"method":"listModels"})
        if result['status_code'] >= 200 and result['status_code'] < 300:
            return self.pelion_last_cmd_result()
        else:
            return result

    # LoadModel
    def pelion_load_model(self,model_name,s3_filename):
        req_id = str(uuid.uuid4())
        result = self.__pelion_post(req_id,self.pelion_rpc_request_lwmwm_uri, {"jsonrpc":"2.0","id":req_id,"method":"loadModel","params":{"name":model_name,"s3_filename":s3_filename}})
        if result['status_code'] >= 200 and result['status_code'] < 300:
            return self.pelion_last_cmd_result()
        else:
            return result

    # UnloadModel
    def pelion_unload_model(self,model_name):
        req_id = str(uuid.uuid4())
        result = self.__pelion_post(req_id,self.pelion_rpc_request_lwmwm_uri, {"jsonrpc":"2.0","id":req_id,"method":"unloadModel","params":{"name":model_name}})
        if result['status_code'] >= 200 and result['status_code'] < 300:
            return self.pelion_last_cmd_result()
        else:
            return result
    
    # ReloadModel
    def pelion_reload_model(self,model_name,s3_filename):
        req_id = str(uuid.uuid4())
        result = self.__pelion_post(req_id,self.pelion_rpc_request_lwmwm_uri, {"jsonrpc":"2.0","id":req_id,"method":"reloadModel","params":{"name":model_name,"s3_filename":s3_filename}})
        if result['status_code'] >= 200 and result['status_code'] < 300:
            return self.pelion_last_cmd_result()
        else:
            return result

    # Predict
    def pelion_predict(self,model_name,input_data_url,output_url):
        req_id = str(uuid.uuid4())
        result = self.__pelion_post(req_id,self.pelion_rpc_request_lwmwm_uri,{"jsonrpc":"2.0","id":req_id,"method":"predict","params":{"model_name":model_name,"input_data_url":input_data_url,"output_url":output_url}})
        if result['status_code'] >= 200 and result['status_code'] < 300:
            return self.pelion_last_cmd_result()
        else:
            return result
    
    
#
# Pelion Sagemaker Notebook Helper Class    
#
class MyNotebook:
    def __init__(self, api_key, device_id, endpoint_api, aws_s3_folder, async_response_sec=0.25):
        # Initialize Sagemaker
        self.sagemaker_init(aws_s3_folder)
        
        # Initialize Pelion Sagemaker Controller API
        self.pelion_sagemaker_controller_init(api_key, device_id, endpoint_api, async_response_sec)
    
    # Sagemaker Init()
    def sagemaker_init(self,aws_s3_folder):
        print("")
        print("Initializing Sagemaker and S3...")
        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')
        for bucket in self.s3.buckets.all():
            print('Target Bucket: ' + bucket.name)

        self.role = get_execution_role()
        self.sess = sagemaker.Session()
        self.region = boto3.Session().region_name
        self.sagemaker_client = boto3.client('sagemaker', region_name=self.region)

        # S3 bucket and folders for saving model artifacts.
        # Feel free to specify different bucket/folders here if you wish.
        self.bucket = self.sess.default_bucket()
        print('Default Bucket: ' + self.bucket)
        self.folder = aws_s3_folder
        self.compilation_output_sub_folder = self.folder + '/compilation-output'
        self.iot_folder = self.folder + '/iot'

        # S3 Location to save the model artifact after compilation
        self.s3_compilation_output_location = 's3://{}/{}'.format(self.bucket, self.compilation_output_sub_folder)

        # Display the S3 directories used
        print("")
        print("Compiled Models Location: " + self.s3_compilation_output_location)
        print("IoT Input/Output Folder: " + 's3://{}/{}'.format(bucket, self.iot_folder))
        
    # Pelion Sagemaker Controller Init()
    def pelion_sagemaker_controller_init(self, api_key, device_id, endpoint_api = 'api.us-east-1.mbedcloud.com', async_response_sec=0.25):
        print("")
        print("Initializing Pelion Sagemaker Controller. Pelion API: " + endpoint_api + " Pelion Sagemaker Edge Agent PT DeviceID: " + device_id)
        
        # Create an instance of the Controller API...
        self.pelion_api = ControllerAPI(api_key,device_id,endpoint_api, async_response_sec)
        
        # Sync the configuration to match our sagemaker config
        print("")
        print("Syncing Pelion Configuration to match Sagemakers...")
        result = self.pelion_api.pelion_set_config('awsS3Bucket',self.bucket)
        if result['status_code'] >= 200 and result['status_code'] < 300:
            result = self.pelion_api.pelion_set_config('awsS3ModelsDirectory',self.compilation_output_sub_folder)
            if result['status_code'] >= 200 and result['status_code'] < 300:
                result = self.pelion_api.pelion_set_config('awsS3DataDirectory',self.iot_folder)
                if result['status_code'] >= 200 and result['status_code'] < 300:
                    result = self.pelion_api.pelion_set_config('awsRegion',self.region)
        if result['status_code'] >= 200 and result['status_code'] < 300:
            print("")
            print("Configuration Sync SUCCESS. Current Pelion Configuration:")
            print(self.pelion_api.pelion_get_config())
        else:
            print("")
            print("Configuration Sync FAILED with code: " + str(result['status_code']))
            print("Please confirm Edge Agent PT DeviceID and Edge gateway availability and retry...")
            
    # Save off the model
    def save_model(self, model_basename):
        # self.model.save(model_basename + '.h5')
        tf.keras.models.save_model(self.model,model_basename + '.h5')
        
        with tarfile.open(model_basename + '.tar.gz', mode='w:gz') as archive:
            archive.add(model_basename + '.h5')
        
        return model_basename + '.tar.gz'
        
    # Compile model and package/upload to S3
    def compile_model(self, created_model, target_device, model_basename, framework, data_shape):
        # Announce long winded task
        print("")
        print("Beginning model compilation...")
        
        # Record the allocated model
        self.model = created_model;
        
        # Save off the model
        packaged_model_filename = self.save_model(model_basename)

        sagemaker_client = boto3.client('sagemaker', region_name=self.region)
        keras_model_path = self.sess.upload_data(packaged_model_filename, self.bucket, self.folder)

        keras_compilation_job_name = 'Sagemaker-Edge-'+ str(time.time()).split('.')[0]
        
        # Initiate the compilation job
        print("")
        print('Compilation job (%s) has started...' % keras_compilation_job_name)
        response = sagemaker_client.create_compilation_job(
                CompilationJobName=keras_compilation_job_name,
                RoleArn=self.role,
                InputConfig={
                    'S3Uri': keras_model_path,
                    'DataInputConfig': data_shape,
                    'Framework': framework.upper()
                },
                OutputConfig={
                    'S3OutputLocation': self.s3_compilation_output_location,
                    'TargetDevice': target_device 
                },
                StoppingCondition={
                    'MaxRuntimeInSeconds': 1900
                }
            )

        print(response)

        # Poll every 30 sec
        while True:
            response = sagemaker_client.describe_compilation_job(CompilationJobName=keras_compilation_job_name)
            if response['CompilationJobStatus'] == 'COMPLETED':
                break
            elif response['CompilationJobStatus'] == 'FAILED':
                print(str(response))
                raise RuntimeError('Compilation failed')
            print('Compiling ...')
            time.sleep(10)
        print('Done!')
        return keras_compilation_job_name

    # package up the model as tgz for transport via Pelion to Sagemaker Edge Agent service
    def package_model(self, keras_packaged_model_name, keras_model_version, keras_compilation_job_name):
        # Announce long winded task
        print("Beginning model packaging...")
        
        # Create the model_package name that we will use
        self.model_package = '{}-{}.tar.gz'.format(keras_packaged_model_name, keras_model_version)
        
        # Create the packaging job... 
        keras_packaging_job_name=keras_compilation_job_name+"-packaging"
        response = self.sagemaker_client.create_edge_packaging_job(
            RoleArn=self.role,
            OutputConfig={
                'S3OutputLocation': self.s3_compilation_output_location,
            },
            ModelName=keras_packaged_model_name,
            ModelVersion=keras_model_version,
            EdgePackagingJobName=keras_packaging_job_name,
            CompilationJobName=keras_compilation_job_name
        )

        print(response)

        # Poll every 30 sec
        while True:
            job_status = self.sagemaker_client.describe_edge_packaging_job(EdgePackagingJobName=keras_packaging_job_name)
            if job_status['EdgePackagingJobStatus'] == 'COMPLETED':
                break
            elif job_status['EdgePackagingJobStatus'] == 'FAILED':
                raise RuntimeError('Edge Packaging failed')
            print('Packaging ...')
            time.sleep(30)
        print('Done!')
        return self.model_package
    
    # Copy our prediction results back to our notebook from S3...
    def copy_results_to_notebook(self, output_tensor_url, local_output_tensor_filename):
        output_tensor_filename = output_tensor_url.replace('s3://','')
        print("Retrieving Output Tensor from S3: " + output_tensor_url + ". Saving locally to: " + local_output_tensor_filename + "...")
        with open(local_output_tensor_filename, 'wb') as f:
            self.s3_client.download_fileobj(self.bucket, output_tensor_filename, f)
    
    # Simple Image List Display with optional annotations...
    def display_images(self, my_list, most_likely_labels=None):
        for i, img in enumerate(my_list):
            display(img)
            if most_likely_labels != None:
                if i < len(most_likely_labels):
                    pred = most_likely_labels[i]
                    pred_tuple = pred[0]
                    pred_name = pred_tuple[1]
                    pred_percent = round(pred_tuple[2]*100.0,3)
                    print("Predicted Image Contents: \"" + pred_name + "\" Confidence: " + str(pred_percent) +"%")
                else:
                    print("Predicted Image Contents not calculated: models compiled-in input shape length set too small for current dataset")
            print("")

    # Read in a batch of images
    def read_image_batch(self, img_paths, img_height, img_width):
        img_list = [load_img(img_path, target_size=(img_height, img_width)) for img_path in img_paths if os.path.isfile(img_path)]
        array_list =  np.array([img_to_array(img) for img in img_list])
        return {"img":img_list, "array":array_list}
    
    # Save the input tensor for the sagemaker edge adgent PT to read in and pass to the AWS edge agent manager
    def save_input_tensor_to_s3(self, input_tensor, input_data_filename):
        # the Pelion edge agent PT expects the input tensor file to be organzed as a JSON
        input_data_json = {}
        input_data_json ['b64_data'] = base64.b64encode(input_tensor.numpy().data.tobytes()).decode('ascii')

        # Save the input tensor JSON data...
        print("Saving input tensor to file: " + input_data_filename)
        with open(input_data_filename, 'w') as f:
            f.write(json.dumps(input_data_json))
            f.close()
            
        # Upload the images in the list to S3
        print("")
        print('Uploading saved input tensor to ' + self.iot_folder + " in S3 bucket " + self.bucket + ' as: ' + input_data_filename + "...")
        print("")
        self.sess.upload_data(input_data_filename, self.bucket, self.iot_folder)
            
    # Method to Decode ResNet50 based predictions
    def decode_resnet50_predictions(self, preds, top=5, class_list_path=None):
        if len(preds.shape) != 2 or preds.shape[1] != 1000:
            raise ValueError('`decode_predictions` expects '
                         'a batch of predictions '
                         '(i.e. a 2D array of shape (samples, 1000)). '
                         'Found array with shape: ' + str(preds.shape))
        class_index = json.load(open(class_list_path))
        results = []
        for pred in preds:
            top_indices = pred.argsort()[-top:][::-1]
            result = [tuple(class_index[str(i)]) + (pred[i],) for i in top_indices]
            result.sort(key=lambda x: x[2], reverse=True)
            results.append(result)
        return results
    
    # Pull the output tensor from s3 back into the notebook and parse/read it into a numpy...
    def get_output_tensor(self, s3_filename, local_nb_filename, tensor_dtype=np.float32):
        # Copy the results back to our notebook
        self.copy_results_to_notebook(s3_filename,local_nb_filename)

        # Read in the output tensor file, convert it, then decode our predictions and display our results...
        print("Opening Output Tensor File: " + local_nb_filename + "...")
        file_size = os.path.getsize(local_nb_filename)
        print("Output Tensor File Size: " + str(file_size) + " bytes")
        with open(local_nb_filename, 'r') as file:
            # Load the JSON-based tensor from its file in our notebook... 
            json_tensor = json.loads(file.read())

            # Convert the (Pelion PT specific) JSON-based tensor to an Numpy Tensor with the intended shape and dtype
            uint8_buffer = base64.b64decode(json_tensor['b64_data'])
            output_tensor = np.frombuffer(uint8_buffer, dtype=tensor_dtype)
            output_tensor_reshaped = np.reshape(output_tensor,(json_tensor['shape'][0],json_tensor['shape'][1]))

            # Display the prediction result tensor details...
            print("Output Tensor (Reshaped) - Shape: " + json.dumps(output_tensor_reshaped.shape) + " Type: " + str(output_tensor_reshaped.dtype))
            return output_tensor_reshaped