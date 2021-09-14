import gitlab
import os
import sys

class terradoc:
    def __init__(self,folder,git_url,gitlab_token):
        self.git_url =git_url
        self.gitlab_token =gitlab_token
        self.f ="None"
        self.folder =folder
        self.subgrouplist =[]
        self.git_url =git_url

        self.gl = gitlab.Gitlab(git_url,private_token = gitlab_token)

        if not os.path.isdir(os.getcwd()+self.folder+"/reports/modules"):
            os.makedirs(os.getcwd()+self.folder+"/reports/modules")
        self.f = open(os.getcwd()+self.folder+'/reports/modules/README.md', 'w')
        sys.stdout = self.f
        print( "group-name | module-name | tag |")
        print("--- | --- | --- |")

    def myMax(self,liste):
        max = liste[0]
        for x in liste:
            if x > max :
                max = x
        return max
    def getSubgroupList(self,group):

        group = self.gl.groups.get(group)
        self.subgrouplist = group.subgroups.list()
        return  self.subgrouplist
    def getModule(self, subgrouplist,group):
        groupob = self.gl.groups.get(group)
        for subgroupe in subgrouplist:
            sub=self.gl.groups.get(subgroupe.id).subgroups.list()

            if sub:
                self.getModule(sub)

            projects = self.gl.groups.get(subgroupe.id).projects.list()
            for project in projects:
                tags = self.gl.projects.get(project.id).tags.list()
                taglist =[]
                for tag in tags:
                    tagname= tag.name
                    taglist.append(tagname)
                if not  taglist :
                    print(str(subgroupe.web_url[(subgroupe.web_url.index(groupob.name)):len(subgroupe.web_url)])+ "|" +project.name +" | no tags")

                else :
                    print(str(subgroupe.web_url[(subgroupe.web_url.index(groupob.name)):len(subgroupe.web_url)])+ "|" +project.name +  "|" +self.myMax(taglist))
        if not self.subgrouplist:
            groupob= self.gl.groups.get(group)
            projects = groupob.projects.list()
            for project in projects:
                tags = self.gl.projects.get(project.id).tags.list()
                taglist =[]
                for tag in tags:
                    tagname= tag.name
                    taglist.append(tagname)
                if not  taglist :
                    print(str(groupob.web_url[(groupob.web_url.index(groupob.name)):len(groupob.web_url)])+ "|" +project.name +" | no tags")

                else :
                    print(str(groupob.web_url[(groupob.web_url.index(groupob.name)):len(groupob.web_url)])+ "|" +project.name +  "|" +self.myMax(taglist))
