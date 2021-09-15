import json
import re
import os

class TestConfiguration(object):

    def __init__(self, path):
        with open(path, 'r') as json_file:
            json_text = json_file.read()
            variables = re.findall(r"\$\{[A-Za-z_-]+\}", json_text)
            for variable in variables:
                varname = variable.replace('$','').replace('{','').replace('}','')
                try:
                    json_text = json_text.replace(variable,os.environ[varname])
                except: raise Exception("Variable " + varname + " is undefined")
            self.testConfig = json.loads(json_text)
        for test in self.testConfig["tests"]:
            if "bcoCheck" in test:
                test["conditions"] = test["conditions"] + self.getDefaultBcoConditions()
            if "stdoutCheck" in test:
                test["conditions"] = test["conditions"] + self.getDefaultStdoutConditions()

    def getConfiguration(self):
        return self.testConfig

    def getDefaultBcoConditions(self):
        bcoConditions = [{
                    "file":"bco",
                    "name":"Bco exists",
                    "error_message":"Bco does not exist",
                    "command":"echo $file"
                },
                {
                    "file":"bco",
                    "name":"Provenance domain exists and is not empty",
                    "error_message":"Provenance domain not found in bco or is empty",
                    "command":"grep -q -m1 provenance_domain $file && jq -e 'if (.provenance_domain | length) == 0 then false else true end' $file"
                },
                {
                    "file":"bco",
                    "name":"Execution domain exists and is not empty",
                    "error_message":"Execution domain not found in bco or is empty",
                    "command":"grep -q -m1 execution_domain $file && jq -e 'if (.execution_domain | length) == 0 then false else true end' $file"
                },
                {
                    "file":"bco",
                    "name":"Parametric domain exists and is not empty",
                    "error_message":"Parametric domain not found in bco or is empty",
                    "command":"grep -q -m1 parametric_domain $file && jq -e 'if (.parametric_domain | length) == 0 then false else true end' $file"
                },
                {
                    "file":"bco",
                    "name":"Description domain exists and is not empty",
                    "warning":True,
                    "command":"grep -q -m1 description_domain $file && jq -e 'if (.description_domain | length) == 0 then false else true end' $file"
                }]
        return bcoConditions

    def getDefaultStdoutConditions(self):
        stdoutConditions = [    
                {
                    "file":"stdout_log",
                    "name":"Stdout exits",
                    "command":"test -f $file"
                }]
        return stdoutConditions
