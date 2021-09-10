#!/user/bin/env python3 
"""
uniboost.py: This program is used for Rancher purposes.
Requirements: python2.7 or later.
"""

__author__ = "Michael Shobitan"
__copyright__ = "Copyright 2019, BTCS Platform Engineering"
__credits__ = ["Michael Shobitan"]
__license__ = "PFE"
__version__ = "0.2.1"
__maintainer__ = "Michael Shobitan"
__email__ = "michael.shobitan@pfizer.com"
__status__ = "Development"

import os
import re
import sys
import json
import time
import boto3
import atexit
import shutil
import urllib3
import argparse
import requests
import subprocess
import boto.ec2.autoscale
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'Content-type':'application/json'}

def exampleFunc():
    """ 
    Summary line. 
  
    Extended description of function. 
  
    Parameters: 
    arg1 (int): Description of arg1 
  
    Returns: 
    int: Description of return value 
    """

    pass


def latest():
    script = subprocess.Popen(["pip", "install", "uniboost", "-U"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    this_out, this_err = script.communicate()
    return this_out

def clusterInfo(url, key, secret):
    response = requests.get(url, auth=(key, secret), headers=headers, verify=False)
    binary = response.content
    output = json.loads(binary)

    return {'response': response, 'binary': binary, 'output': output}

def set_env_var(var_name, var_value):
    os.environ[var_name] = var_value
    
def get_env_var(var_name):
    path = os.environ[var_name]
    return path

def file_to_json(json_file):
    with open(json_file, 'r') as handle:
        parsed = json.load(handle)
    return parsed

def jsonPP(json_content):
    response = json.dumps(json_content, indent=4)
    return response

def ppJSON(json_content):
    response = json.dumps(json_content, indent=4, sort_keys=True, default=str)
    return response

def cd(cd_dir):
    os.chdir(cd_dir)

def pwd():
    cwd = os.getcwd()
    return cwd

def file_exist(this_file):
    status = os.path.exists(this_file)
    if(status == True):
        if(os.path.isdir(this_file)):
            file_type = 'directory'
            # print(file_type)
        elif(os.path.isfile(this_file)):  
            file_type = 'file'
            # print(file_type)
        else:
            print("It is a special file (socket, FIFO, device file, etc.)" )
        status = 'exist'
    else:
        file_type = status
        status = status

    return {'file_type': file_type, 'status': status}

def delete_folder(folder_name):
    try:
        os.rmdir(folder_name)
    except OSError:
        print ("NOTE: Deletion of the directory %s failed" % folder_name + "\n")
    else:
        print ("NOTE: Successfully deleted the directory %s" % folder_name)

# def cluster_deletion():
#     env_clusters_url = env_url + "/clusters"
#     # projects_request = UrlRequest(env_clusters_url, key, secret)
#     # output = projects_request.output
        
#     response = requests.get(env_clusters_url, auth=(key, secret), headers=headers, verify=False)
#     binary = response.content
#     output = json.loads(binary)

#     for counter in range(len(output['data'])):
#         cluster_name = output['data'][counter]['name']           
#         if(folder_name == cluster_name):
#             cluster_id = output['data'][counter]['id']
#             cluster_delete_url = "%s/%s" % (env_clusters_url, cluster_id)
#             cluster_delete_url = cluster_delete_url[:4] + 's' + cluster_delete_url[4:]
#             cluster_delete_url = "curl -u \"%s:%s\" -X DELETE -H 'Accept: application/json' '%s'" % (key, secret, cluster_delete_url)
#             p = subprocess.Popen([cluster_delete_url], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             out, err = p.communicate()

# cluster_detected =  False
# def cluster_detection(url):
#     global cluster_detected
#     url = url + "/clusters"
#     # projects_request = UrlRequest(env_clusters_url, key, secret)
#     # output = projects_request.output
        
#     response = requests.get(url, auth=(key, secret), headers=headers, verify=False)
#     binary = response.content
#     output = json.loads(binary)

#     for counter in range(len(output['data'])):
#         cluster_name = output['data'][counter]['name']           
#         if(folder_name == cluster_name):
#             cluster_id = output['data'][counter]['id']
#             cluster_detected = True
#             print("ERROR: Cluster already exist!")
#             cd(folder_name)
#             shutil.rmtree(folder_name, ignore_errors=True)
#             print('NOTE: Cluster folder cleaning complete')
#             # cluster_deletion()
#             sys.exit()

# cluster_detection()        

def awsAPIConnection():
    conn = boto.ec2.autoscale.connect_to_region(get_env_var('AWS_REGION'),
    aws_access_key_id=get_env_var('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=get_env_var('AWS_SECRET_ACCESS_KEY'))
    return conn

def eks():
    eks = boto3.client('eks')
    return eks

def describe_cluster(eks, cluster):
    response = eks.describe_cluster(
        name=cluster
    )
    return response

def cloudformation():
    cloudformation = boto3.client('cloudformation')
    return cloudformation

def describe_stack(cloudformation, cluster):
    stack_name = "%s-eks-worker-nodes" % (cluster)
    response = cloudformation.describe_stacks(
        StackName=stack_name,
    )
    return response

def describe_stack_dynamically(cloudformation, cluster):
    response = cloudformation.describe_stacks()

    clusterStackNames = []
    stacksINFO = []
    # for counter in xrange(len(response['Stacks'])): # Python2.7
    for counter in range(len(response['Stacks'])): # Python3.6
        stackName = response['Stacks'][counter]['StackName']
        if(cluster in stackName):
            clusterStackNames.append(stackName)
            # print(response['Stacks'][counter])
            stacksINFO.append(response['Stacks'][counter])
            # print(json.dumps(response['Stacks'][counter], indent=4, sort_keys=True, default=str))

    return {'clusterStackNames': clusterStackNames, 'stacksINFO': stacksINFO}

def cahc(cluster):
    eks = eks()
    clusterINFO = describe_cluster(eks, cluster)
    # Enabled
    privateAccess = clusterINFO['cluster']['resourcesVpcConfig']['endpointPrivateAccess']
    # Disabled
    publicAccess = clusterINFO['cluster']['resourcesVpcConfig']['endpointPublicAccess']

    cloudformation = cloudformation()
    clusterStackINFO = describe_stack(cloudformation, cluster)
    for instance in xrange(len(clusterStackINFO['Stacks'][0]['Parameters'])):
        parameterKey = (clusterStackINFO['Stacks'][0]['Parameters'][instance]['ParameterKey'])
        if(parameterKey == 'PublicIp'):
            # False
            PulicIpValue = (clusterStackINFO['Stacks'][0]['Parameters'][instance]['ParameterValue'])
    
    return {'privateAccess': privateAccess, 'publicAccess': publicAccess, 'PulicIpValue': PulicIpValue}

def times():
    day = time.strftime("%A")
    month = time.strftime("%B")
    date = time.strftime("%d %H:%M:%S")
    year = time.strftime("%Y")

    return {'day': day, 'month': month, 'date': date, 'year': year}

printLogMsg = False
def logger(logFile, logMsg, printLogMsg, newLine):
    """ 
    Logger for calling program. 
    
    Parameters:
    logFile (str): File to be logged to
    logMsg (str): Message to be logged
    printLogMsg (bool): Option to print log message
    newLine (str): Option to prepend newline to the top, both or bottom only
  
    Returns: 
    int: Description of return value 
    """

    if(printLogMsg is True):
        print(logMsg)

    program = sys.argv[0]
    program = program.rsplit('/', 1)[-1]\
    
    if(newLine == 'top'):
        logFile.write('\n' + str(program) + " " + str(times()['day'][:3]) + " " + str(times()['month'][:3]) + " " + str(times()['date']) + " " + str(time.tzname[0]) + " " + str(times()['year']) + " - " + str(logMsg))    
    elif(newLine == 'both'):
        logFile.write('\n' + str(program) + " " + str(times()['day'][:3]) + " " + str(times()['month'][:3]) + " " + str(times()['date']) + " " + str(time.tzname[0]) + " " + str(times()['year']) + " - " + str(logMsg) + '\n')   
    elif(newLine == 'bottom'):
        logFile.write(str(program) + " " + str(times()['day'][:3]) + " " + str(times()['month'][:3]) + " " + str(times()['date']) + " " + str(time.tzname[0]) + " " + str(times()['year']) + " - " + str(logMsg) + '\n')