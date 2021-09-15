import json
import re
import os
import time
import logging
import subprocess
import threading
import time
import socket

class TestRunner(object):

    def __init__(self, configuration, cromwell, index = -1):
        self.logger = logging.getLogger(__name__)
        self.configuration = configuration
        self.cromwell = cromwell
        self.index = index
        self.exitCode = 0
        maxThreads = 1
        if "threads" in self.configuration:
            maxThreads = self.configuration["threads"]
        self.sema = threading.Semaphore(value = maxThreads)

    def run(self):
        self.logger.debug("Cromwell started")
        testIndex = 0
        self.logger.debug("Index " + str(self.index))
        
        threads = list()
        for testJson in self.configuration["tests"]:
            thread = threading.Thread(target = self.runTest, args=(testIndex, testJson))
            threads.append(thread)
            thread.start()
            time.sleep(2)
            testIndex = testIndex + 1
        for thread in threads:
            thread.join()
        return self.exitCode

    def runTest(self, testIndex, testJson):
        self.sema.acquire()
        exitCode = 0
        generictext = "Test (idx " + str(testIndex) + "; " + str(testJson["name"]) + ")"
        if self.index != -1 and self.index != testIndex:
            self.logger.info("Excluding test with index " + str(testIndex))
            self.logger.info("Excluded test " + str(testJson["name"]))
            self.sema.release()
            return 0
        if ("hostnames" in testJson):
            if not (socket.gethostname() in testJson["hostnames"]):
                self.logger.info("Excluding test because of hostname mismatch " + str(socket.gethostname()))
                self.logger.info("Excluded test " + str(testJson["name"]))
                self.sema.release()
                return 0
        try:
            self.logger.info("Test name: " + str(testJson["name"]))
            if not "inputs" in testJson:
                testJson["inputs"] = dict()
            self.cromwell.submitJob(self.configuration["wdl"], testJson["inputs"], str(testIndex))
            status = "Started"
            start = time.time()
            while status != "Failed" and status != "Succeeded":
                time.sleep(1)
                previousStatus = status
                status = self.cromwell.getStatus()
                if status != previousStatus:
                    start = time.time()
                    if previousStatus != "Started": print()
                diff = int(time.time() - start)
                print("Cromwell job status " + status + " " + str(diff) + "s                     ", end ="\r")
            print()
            if "expecterror" in testJson and testJson["expecterror"]:
                if self.cromwell.returnCode > 0:
                    self.logger.info("[PASSED] test finished with expected Error")
                else:
                    self.logger.error("[ERROR] test succeded but expected failed")
                    exitCode = errorExitCode
                testJson["conditions"] = []
            for condition in testJson["conditions"]:
                errorText = "[ERROR]"
                errorExitCode = 1
                if "warning" in condition:
                    if condition["warning"]:
                        errorText = "[WARNING]"
                        errorExitCode = 0
                try:
                    if self.cromwell.getPathToOutput(condition["file"]) == 'missing':
                        self.logger.error(errorText + " " + generictext + " '" + condition["name"] + "' failed with message: no " + condition["file"] + " file in workflow outputs")
                        exitCode = errorExitCode
                    else:
                        bashCommand = condition["command"].replace("$file", self.cromwell.getPathToOutput(condition["file"]))
                        if "index" in condition:
                            bashCommand = condition["command"].replace("$file", self.cromwell.getPathToOutput(condition["file"], condition["index"]))
                        process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        output, error = process.communicate()
                        output = output.decode("utf-8").strip() + error.decode("utf-8").strip()
                        returnCode = process.poll()
                        if returnCode == 0:
                            self.logger.info("[PASSED] " + generictext + " '" + condition["name"] + "'")
                        else:
                            if "error_message" in condition.keys():
                                self.logger.error(errorText + " " + generictext + " '" + condition["name"] + "' failed with message: " + condition["error_message"])
                            else:
                                self.logger.error(errorText + " " + generictext + " '" + condition["name"] + "' failed")
                            exitCode = errorExitCode
                
                except Exception as e:
                    self.logger.error(errorText + " " + generictext + " '" + condition["name"] + "' failed because file " + condition["file"] + " does not exists. " + e)
                    exitCode = errorExitCode
                    
        except Exception as e:
            exitCode = 1
            print("ERROR " + str(e))
            self.cromwell.stop()   
            self.sema.release()
        if (exitCode != 0 and self.exitCode == 0):
            self.exitCode = exitCode       
        self.sema.release()
