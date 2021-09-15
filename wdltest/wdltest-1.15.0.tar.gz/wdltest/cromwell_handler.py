import subprocess
import requests
import os
import logging
import threading
import socket
import random
import time
import json
import regex
import getpass ## for username
from shutil import copyfile
from datetime import datetime

class CromwellHandler(object):

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.checkJava()
        self.downloadCromwell()
        self.mode = self.config['cromwell']['mode']

    def checkJava(self):
        self.logger.debug('Checking if java is installed')
        bashCommand = "java -version"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode("utf-8").strip() + error.decode("utf-8").strip()
        if(not (("vm" in output) or ("VM" in output))):
            raise Exception("JVM is not installed")

    def downloadCromwell(self):
        dir = self.config['paths']['dir']
        if(not os.path.isdir(dir)):
            os.mkdir(dir)
            os.chmod(dir, 0o776)
        path = dir + "/cromwell.jar"
        url = self.config['cromwell']['url']
        if(not os.path.isfile(path)):
            self.logger.debug('Downloading cromwell')
            request = requests.get(url, allow_redirects=True)
            open(path, 'wb').write(request.content)
            os.chmod(path, 0o666)
        configSourcePath = os.path.dirname(__file__) + "/cromwell.cfg"
        configDestinationPath = dir + "/cromwell.cfg" 
        if(not os.path.isfile(configDestinationPath)):
            copyfile(configSourcePath, configDestinationPath)
            os.chmod(configDestinationPath, 0o666)

    def submitJob(self, wdl, inputs, id):
        self.logger.debug("Submmitting job in " + self.mode + " mode")
        self.basePath = self.config['paths']['dir'] + "/" + getpass.getuser() + "/" + os.path.basename(os.path.dirname(wdl))
        if(not os.path.isdir(self.basePath)):
            os.makedirs(self.basePath)
            os.chmod(self.basePath, 0o776)
        runPath = self.basePath + "/" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "/" + id
        if(not os.path.isdir(runPath)):
            os.makedirs(runPath)
            os.chmod(runPath, 0o776)
        self.inputPath = runPath + "/inputs.json"
        logPath = runPath + "/cromwell-execution.log"

        self.returnCode = -1
        self.logger.debug("PATH: " + runPath)
        with open(self.inputPath, "w") as inputs_file:
            print(json.dumps(inputs), file=inputs_file)
        bashCommand = "java -Dconfig.file=" + self.config['paths']['dir'] + "/cromwell.cfg" + " -jar " + self.config['paths']['dir'] + "/cromwell.jar run " + wdl + " --inputs " + self.inputPath
        self.cromwellProcess = subprocess.Popen(bashCommand.split(), cwd=runPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.log = ""
        self.status = "Running"
        with open(logPath, "w") as log_file:
            for line in iter(self.cromwellProcess.stdout.readline, ""):
                printline = line.decode("utf-8").replace('\n', '')
                if "to Done" in printline:
                    print(printline)
                print(printline, file=log_file)
                self.log = self.log + line.decode("utf-8").replace('\n', '')
                if "workflow finished with status" in printline:
                    self.status = printline.split()[-1].replace("'", '').replace('.',' ')
                if line == b'' and self.cromwellProcess.poll() is not None:
                    break

        if "Succeeded" in self.status:
            pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
            jsons = pattern.findall(self.log)
            for jsonitem in jsons:
                if jsonitem.find('"outputs":') != -1:
                    rawoutputs = json.loads(jsonitem)
            rawoutputs = rawoutputs["outputs"]
            self.outputs = dict()
            for key in rawoutputs:
                if not isinstance(rawoutputs[key], list):
                    rawoutputs[key] = str(rawoutputs[key])
            for key in rawoutputs:
                try:
                    self.outputs[key.split('.')[-1]] = rawoutputs[key]
                except Exception as e:
                    self.logger.debug("error: " + str(e))
            self.cromwellProcess.stdout.close()
            self.returnCode = self.cromwellProcess.wait()
            self.logger.debug("Finished run")
            self.logger.info("Path to log " + logPath)
        else:
            self.outputs = dict()
            self.cromwellProcess.stdout.close()
            self.logger.info("Workflow failed")
            self.logger.info("Path to log " + logPath)
            self.cromwellProcess.wait()
            self.returnCode = self.cromwellProcess.returncode

    def getStatus(self):
        if self.returnCode == -1:
            return "Running"
        if self.returnCode == 0:
            return "Succeeded"
        if self.returnCode > 0:
            return "Failed"

    def getPathToOutput(self, desiredOutput, index = 0):
        if desiredOutput in self.outputs:
            output = self.outputs[desiredOutput]
            if "list" in type(output).__name__:
                return output[index]
            return output
        else:
            return 'missing'
            

    def stop(self):
        pass