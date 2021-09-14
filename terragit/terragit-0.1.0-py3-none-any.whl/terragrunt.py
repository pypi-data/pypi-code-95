import signal
import subprocess
import sys
from os import listdir
from os.path import isdir, join
import gitlab
import os
import pathlib


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class terragrunt :
    def __init__(self,verbose):

        self.pathList=[]
        self.failedloglist=[]
        self.logfileName =[]
        self.state_list =""
        self.logsFolder=""
        self.failedlogsFolder =""
        self.verbose=verbose
        if self.verbose:
            if not os.path.isdir(os.getcwd()+"/logs"):
                os.makedirs(os.getcwd()+"/logs")
            if not os.path.isdir(os.getcwd()+"/failedlogs"):
                os.makedirs(os.getcwd()+"/failedlogs")
            self.logsFolder=pathlib.Path("logs").absolute().as_posix()
            self.failedlogsFolder =pathlib.Path("failedlogs").absolute().as_posix()

    def getAllFolder(self,path):
        if  path in self.pathList:
            return
        else:

            only_tf_files=[f for f in  sorted(listdir(path)) if not isdir(join(path, f)) and f.endswith('.tf')]
            if len(only_tf_files)==0:
                onlyDirectories = [d for d in sorted(listdir(path)) if isdir(join(path, d)) and d !=".terraform" and d != ".terragrunt-cache"]
                if(len(onlyDirectories) > 0):
                    for i in range(0, len(onlyDirectories)):
                        self.getAllFolder(path+"/"+onlyDirectories[i])
            else :
                self.pathList.append(path)
        return self.pathList

    def executeTerragrunt(self,command ,path,logsFolder,verbose):
         logfileName=path.split("live/")[1].replace("/","_")
         profile = "dev02"
         if("20-int" in path) : profile = "int"
         if("30-uat" in path) : profile = "uat"
         if("31-uatm" in path) : profile = "uat"
         if("32-miscuat" in path) : profile = "miscuat"
         if("42-miscprod" in path) : profile = "miscprod"
         if("40-prod" in path) : profile = "prod"
         if("41-proddr" in path) : profile = "prod"
         if verbose:
            self.state_list = (" export AWS_PROFILE="+profile+" && terragrunt "+command+" -no-color 2>&1 | tee " +logsFolder+"/"+logfileName+".log")
         else:

            self.state_list = (" export AWS_PROFILE="+profile+" && terragrunt "+command+" -no-color  2>&1 ")
         return self.state_list



    def printlog(self,command ,pathList ,logsFolder,verbose):
        for path in pathList:

            print(bcolors.OKBLUE+path+":" +bcolors.ENDC)
            os.chdir(path)
            self.executeTerragrunt(command ,path,logsFolder,verbose)
            popen = subprocess.Popen(self.state_list,stdin = subprocess.PIPE, stdout = subprocess.PIPE, shell = True, encoding = 'utf8')
            lines = popen.communicate(input='\n')[0].split("\n")

            for line in lines:
                if("No changes. Infrastructure is up-to-date." in line):
                    print(bcolors.OKGREEN +"  : No changes. Infrastructure is up-to-date."+ bcolors.ENDC)
                    break
                if("No changes. Your infrastructure matches the configuration." in line):
                    print(bcolors.OKGREEN +"  : No changes. Your infrastructure matches the configuration."+ bcolors.ENDC)
                    break
                if("Plan:" in line):
                    print(bcolors.WARNING +line+ bcolors.ENDC)
                    break
                if ("will be updated in-place" in line):
                    print(line.replace('\n',''))
                if ("will be created" in line):
                    print(line.replace('\n',''))
                if ("must be replaced" in line):
                    print(line.replace('\n',''))
                    lint=lines[(lines.index(line)):(len(lines))]
                    lin=lint[0:(lint.index('\n'))]
                    for l in lin:
                        if ("forces replacement" in l):
                            print(l.replace('\n',''))
                            print(lin[(lin.index(l))+1])
                if ("will be destroyed" in line):
                    print(line.replace('\n',''))
                errors =["Hit multiple errors" , "errors" , "Error"  , "Unable to determine underlying exit code"]

                if any(error in line for error in errors):
                    lint=lines[(lines.index(line)):(len(lines))]
                    for l in lint:
                        print(l.replace('\n',''))
                    print(bcolors.FAIL +" COULDNT PROCESS"+ bcolors.ENDC)
                    self.failedloglist.append(path)
                    break
                if("Success! The configuration is valid" in line):
                    print(bcolors.OKGREEN +"Success."+ bcolors.ENDC)
                    break
                if("Apply complete! Resources:" in line):
                    print(bcolors.OKGREEN + line + bcolors.ENDC)
                    break
                #output  messsage
                if command =="output" :
                    if ("will detect it and remind you to do so if necessary" in line):
                        lin = lines[(lines.index(line)+1):(len(lines))]
                        for l in lin:
                            if ("The state file either has no outputs defined" in l):
                                print(bcolors.WARNING + "  : no outputs defined or all the defined outputs are empty." + bcolors.ENDC)
                                break
                            else:
                                print(l)
                    break

            else:
                print(bcolors.FAIL +" COULDNT PROCESS"+ bcolors.ENDC)
                self.failedloglist.append(path)
