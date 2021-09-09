import os
import sys
import json
import errno
import base64
import requests
import hashlib

from .domain import FlowName, JobBuildNumber, AgentToken, Job, ServerUrl, AgentJobDir, AgentWorkspace

HttpHeaderWithJson = {
    "Content-Type": "application/json",
    "AGENT-TOKEN": AgentToken
}

HttpHeaders = {
    "AGENT-TOKEN": AgentToken
}

def GetVar(name, required=True):
    val = os.environ.get(name)
    if required and val is None:
        sys.exit("{} is missing".format(name))
    return val


def GetCurrentJob():
    return Job()


def ToBase64String(strVal):
    b64bytes = base64.b64encode(strVal.encode("utf-8"))
    return str(b64bytes, 'utf-8')


def FindFiles(file, path=AgentJobDir):
    files = []

    for i in os.listdir(path):
        fullPath = os.path.join(path, i)

        if os.path.isdir(fullPath) and not i.startswith("."):
            files += FindFiles(file, fullPath)

        if os.path.isfile(fullPath) and i == file:
            files.append(fullPath)

    return files


def MD5(path):
    md5Hash = hashlib.md5()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5Hash.update(byte_block)
        return md5Hash.hexdigest()


class Client:
    def __init__(self):
        self.secretPath = os.path.join(AgentWorkspace, '.ci_secret')
        self.initDirs(self.secretPath)

        self.configPath = os.path.join(AgentWorkspace, '.ci_config')
        self.initDirs(self.configPath)
        pass

    def initDirs(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                print('unable to init required dirs')
                raise

    def getCredential(self, name):
        try:
            url = "{}/api/secret/{}".format(ServerUrl, name)
            r = requests.get(url=url, headers=HttpHeaderWithJson)
            return self.handleResponse(r)
        except Exception as e:
            print(e)
            return None

    # download secret file and return file path that saved locally
    def downloadSecretFile(self, name, filename):
        try:
            url = "{}/api/secret/{}/download/{}".format(ServerUrl, name, filename)
            r = requests.get(url, allow_redirects=True, headers=HttpHeaderWithJson)

            if r.status_code == 200:
                path = os.path.join(self.secretPath, filename)
                open(path, 'wb').write(r.content)
                return path

            print(r)
            return None
        except Exception as e:
            print(e)
            return None

    def getConfig(self, name):
        try:
            url = "{}/api/config/{}".format(ServerUrl, name)
            r = requests.get(url=url, headers=HttpHeaderWithJson)
            return self.handleResponse(r)
        except Exception as e:
            print(e)
            return None

    def listFlowUsers(self):
        try:
            url = "{}/api/flow/{}/users".format(ServerUrl, FlowName)
            r = requests.get(url=url, headers=HttpHeaderWithJson)
            return self.handleResponse(r)
        except Exception as e:
            print(e)
            return None

    def sendJobReport(self, path, name, zipped, contentType, entryFile=""):
        try:
            url = "{}/api/flow/{}/job/{}/report".format(
                ServerUrl, FlowName, JobBuildNumber)

            body = {
                "name": name,
                "zipped": zipped,
                "type": contentType,
                "entryFile": entryFile
            }

            r = requests.post(url=url, headers=HttpHeaders, files={
                'file': open(path, 'rb'),
                'body': ('', json.dumps(body), 'application/json')
            })

            return self.handleResponse(r)
        except Exception as e:
            print(e)
            return -1

    def uploadJobArtifact(self, path, srcDir=None):
        try:
            url = "{}/api/flow/{}/job/{}/artifact".format(
                ServerUrl, FlowName, JobBuildNumber)

            body = {
                "md5": MD5(path)
            }

            if srcDir != None:
                body["srcDir"] = srcDir

            r = requests.post(url=url, headers=HttpHeaders, files={
                'file': open(path, 'rb'),
                "body": ('', json.dumps(body), 'application/json')
            })

            return self.handleResponse(r)
        except Exception as e:
            print(e)
            return -1

    def sendStatistic(self, body):
        try:
            url = "{}/api/flow/{}/stats".format(ServerUrl, FlowName)
            r = requests.post(url=url, headers=HttpHeaderWithJson, data=json.dumps(body))
            return self.handleResponse(r)
        except Exception as e:
            print(e)
            return -1

    def addJobContext(self, var):
        try:
            url = "{}/api/flow/{}/job/{}/context".format(ServerUrl, FlowName, JobBuildNumber)
            r = requests.post(url=url, headers=HttpHeaderWithJson, data=json.dumps(var))
            return self.handleResponse(r)
        except Exception as e:
            print(e)
            return -1

    def handleResponse(self, r):
        if r.status_code != 200:
            print(r.text)
            return None

        body = json.loads(r.text)
        if body["code"] != 200:
            print(body["message"])
            return None

        if "data" not in body:
            return body["message"]

        return body["data"]

        
# print(Client().downloadSecretFile("test", "ios_development.cer"))