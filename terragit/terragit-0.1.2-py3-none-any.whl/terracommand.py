import shutil

from terragit.terragrunt import *

class terracommand(terragrunt ,bcolors):
    def __init__(self,idProject,idCommit,idMr,gitlab_token,git_url,directory,verbose,ci_commit_title=""):
        super().__init__(verbose)
        self.idProject= idProject
        self.idCommit=idCommit
        self.idMr =idMr
        self.gitlab_token =gitlab_token
        self.git_url =git_url
        self.ci_commit_title =ci_commit_title
        self.directory=directory
        self.verbose= verbose

    def terragruntCommand(self,command):
        mylist=[]
        if self.directory != None:
            mylist.append(self.directory)
        else:
            gl = gitlab.Gitlab(self.git_url,private_token = self.gitlab_token)
            project = gl.projects.get(self.idProject)
            if  self.idCommit != None:
                commit = project.commits.get(self.idCommit)
                diff = commit.diff()
            if self.idMr != None:
                mr= project.mergerequests.get(self.idMr)
                diff=mr.changes()['changes']
            folderList=[]
            if (len(diff)==0):
                if not isdir(pathlib.Path(self.ci_commit_title).absolute().as_posix()):
                    print(bcolors.FAIL+self.ci_commit_title +" is not valid path"+ bcolors.ENDC)
                else:
                    self.ci_commit_titlePath=pathlib.Path(self.ci_commit_title).absolute().as_posix()
                    self.pathList.append(self.ci_commit_titlePath)
                    self.printlog(command,self.pathList ,self.logsFolder,self.verbose)
            else:
                for change in diff:
                    newPath=change['new_path']
                    if not ("live/") in newPath:
                        print(pathlib.Path(newPath).absolute().as_posix()+bcolors.WARNING +" OUT of SCOPE"+ bcolors.ENDC)
                    else:
                        pathh=pathlib.Path(newPath).parent.absolute().as_posix()
                        folderList.append(pathh)
        
            mylist = list(dict.fromkeys(folderList))


        for path in mylist:
            if(isdir(path)):
                self.getAllFolder(path)
                if command =="changes" :
                    print(mylist)
                    return mylist
        self.printlog(command ,self.pathList ,self.logsFolder ,self.verbose)
        if self.failedloglist:
            if self.verbose:
                for message in self.failedloglist:
                    logfileName=message.split("live/")[1].replace("/","_")
                    os.chdir(self.failedlogsFolder)

                    shutil.move(self.logsFolder+"/"+logfileName+".log", "failed_"+logfileName+".log")
            sys.exit(1)
