import os
from subprocess import Popen, PIPE
from time import sleep

import docker
from termcolor import colored


class Orchestrierung:

    def __init__(self, containerName: str, MustCreate: bool, imageName: str = None, port: int = None,
                 memoryInGB: int = 1, cpuInCores: int = 1, tag: str = "v1"):
        self.containerName = containerName
        self.mustCreate = MustCreate
        self.imageName = imageName
        self.port = port
        self.memoryInGB = memoryInGB
        self.cpuInCores = cpuInCores
        self.tag = tag
        config_file = os.getenv('DB_CONFIG')
        kp_path = os.getenv('KEYPASS')
        conf_r = os.getenv('ENTITY_CONFIGS')

    def startContainer(self):
        try:
            print(colored("Start Container {cn}".format(cn=self.containerName), on_color="on_green"))
            p = Popen(['docker', 'start', self.containerName], stdin=PIPE)
        except:
            print(colored("Container could not be startet {cn}".format(cn=self.containerName), on_color="on_red"))

    def stopContainer(self):
        try:
            print(colored("Stop Container {cn}".format(cn=self.containerName), on_color="on_yellow"))
            p = Popen(['docker', 'stop', self.containerName], stdout=PIPE)

            help = True
            client = docker.from_env()
            while help:
                sleep(1)
                print(client.containers.list(filters={'name': self.containerName}))
                if len(client.containers.list(filters={'name': self.containerName})) == 0:
                    help = False
            print(colored("Stop Container {cn} successfull".format(cn=self.containerName), on_color="on_green"))
        except:
            print(colored("Container could not be stopped {cn}".format(cn=self.containerName), on_color="on_red"))

    def createAndRunContainer(self):
        try:
            print(colored("Create Container {cn}".format(cn=self.containerName + ":" + self.tag), on_color="on_green"))
            if self.port == None:

                p = Popen(['docker', 'run', '-it', '--memory={m}g'.format(m=self.memoryInGB),
                           '--cpus={cpu}'.format(cpu=self.cpuInCores), '-d', '--name',
                           "{c}".format(c=self.containerName),
                           self.imageName + ":" + self.tag],
                          stdout=PIPE)

            else:
                p = Popen(['docker', 'run', '-it', "-p", "{p}:{p}".format(p=self.port),
                           '--memory={m}g'.format(m=self.memoryInGB), '--cpus={cpu}'.format(cpu=self.cpuInCores), '-d',
                           '--name', self.containerName, self.imageName + ":" + self.tag],
                          stdout=PIPE)
            self.startContainer()
        except:
            print(colored("Container could not be createt {cn}".format(cn=self.containerName), on_color="on_red"))

    def runCommandInContainer(self, cmd: str):

        print(colored("Run Command:'{c}' in Container {cn}".format(cn=self.containerName, c=cmd), on_color="on_green"))

        cms = cmd.split(" ")
        c = ['docker', 'exec', self.containerName]
        for e in cms:
            c.append(e)
        p = Popen(c, stderr=PIPE, stdout=PIPE)
        p.communicate()

    def deployDockerImage(self, DockerFilePath: str = ".", ImageName: str = "Test"):
        print(colored("Deploy DockerImage {cn}".format(cn=ImageName), on_color="on_yellow"))
        client = docker.from_env()
        client.images.build(path=DockerFilePath, tag=ImageName + ":" + self.tag)
        print(colored("Image erfolgreich Deployed", on_color="on_green"))
