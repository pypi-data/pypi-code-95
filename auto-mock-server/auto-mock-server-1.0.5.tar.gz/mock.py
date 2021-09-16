

from time import sleep
import os
import subprocess
import platform

import requests
import paramiko


current_directory = os.getcwd()


class Remote_operation():
    def __init__(self,MACHINE_INFO):
        self.ip=MACHINE_INFO["ip"]
        self.port=MACHINE_INFO["port"]
        self.username=MACHINE_INFO["username"]
        self.password=MACHINE_INFO["password"]
        self.sshClient = paramiko.SSHClient()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshClient.connect(self.ip, port=self.port, username=self.username, password=self.password, allow_agent=False)
        self.sftp = self.sshClient.open_sftp()

    def exec_remote_shell(self,cmd):
        '''
        ssh 登录到指定 ip 上,执行命令然后返回执行结果

        :param cmd:
        :param ip:
        :param port:
        :param username:
        :param password:
        :return:
        '''

        stdin, stdout, stderr = self.sshClient.exec_command(cmd, timeout=10000)
        ret = stdout.read()
        ret = bytes.decode(ret)
        return ret

    def ssh_scp_put(self,local_file,remote_file):
        """
        通过ssh上传本地文件到远程服务器

        :param local_file:
        :param remote_file:
        :return:

        example : remote.ssh_scp_put("D:\\toutiaolog\\find\\xigualog_4184087elog_20191113181723.txt","/root/core/xigualog_4184087elog_20191113181723.txt")
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip,self.port, self.username, self.password)
        sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
        sftp = ssh.open_sftp()
        sftp.put(local_file, remote_file)

    def ssh_scp_get(self,local_file, remote_file):
        """
        从远程服务器下载文件到本地

        """

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip, self.port, self.username, self.password)
        sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
        sftp = ssh.open_sftp()
        sftp.get(remote_file, local_file)


class LinuxLocalOperation():
    def start_mock_server(self,mock_server_port):
        self.stop_port_process(mock_server_port)

    def stop_mock_server(self,mock_server_port):
        stop_port_process_cmd = "netstat -ntlp | grep ':"+str(mock_server_port)+" '  |  awk '{print $7}' |  awk -F '/' '{print $1}' | xargs kill -9"
        self.remote_operation.exec_remote_shell(stop_port_process_cmd)


class LinuxRemoteOperation():

    def __init__(self,remote_mock_server_machine):
        self.remote_operation = Remote_operation(remote_mock_server_machine)

    def start_mock_server(self,mock_server_port):
        self.stop_port_process(mock_server_port)
        self.remote_operation.ssh_scp_put("mock_server_code.py", "mock_server_code.py")
        self.remote_operation.exec_remote_shell("nohup python mock_server_code.py > /dev/null   2>&1 &")

    def stop_mock_server(self,mock_server_port):
        stop_port_process_cmd = "netstat -ntlp | grep ':"+str(mock_server_port)+" '  |  awk '{print $7}' |  awk -F '/' '{print $1}' | xargs kill -9"
        self.remote_operation.exec_remote_shell(stop_port_process_cmd)


class WindoxLocalOperation:

    def start_mock_server(self,mock_server_port):
        self.stop_port_process(mock_server_port)
        subprocess.Popen("python  mock_server_code.py",stdout=None)

    def stop_mock_server(self,mock_server_port):
        find_port = 'netstat -aon | findstr %s' % mock_server_port
        result = os.popen(find_port)
        for line in result.readlines():
            pid = line.split(" ")[-1].strip()
            kill_pid_cmd = 'taskkill -f -pid %s' % pid
            subprocess.Popen(kill_pid_cmd)




class MockServerClass:
    """
    创建模拟服务  使用例子：
    mockserver = MockServer(mock_server_machine={"ip":"192.168.3.67","port":"22","username":"root","password":"jiexijiexi@@"},mock_server_port=82)
    mockserver.add_route(route_path="/upgcxcode/18/62/48856218/48856218-1-30015.m4s",response_status='200',response_headers='{"test_key":"test_value"}'
                         ,response_date='{"ok":true,"nodes":["http://192.168.6.135/upgcxcode/29/58/124945829/124945829_nb2-1-30032.m4s"]}')
    mockserver.start_mock_server()

    在 192.168.3.67 启动 一个模拟服务，模拟服务的接口是 /upgcxcode/18/62/48856218/48856218-1-30015.m4s，监听端口是 82，响应状态码是200，响应头包含 "test_key":"test_value"
    响应 内容 是 {"ok":true,"nodes":["http://192.168.6.135/upgcxcode/29/58/124945829/124945829_nb2-1-30032.m4s"]}

    """

    def __init__(self,mock_server_port,remote_mock_server_machine=None):
        """
        :param mock_server_machine:     模拟服务器的登录信息   字典类型 如 {"ip":"192.168.3.67","port":"22","username":"root","password":"jiexijiexi@@"}
        :param mock_server_port:        模拟 服务器的监听端口号， 整形
        """
        self.__route_code_list = []
        self.__remote_mock_server_machine = remote_mock_server_machine
        self.__mock_server_port = mock_server_port

        if self.__remote_mock_server_machine == None:
            if platform.system() == "Windows":
                self.__system_operation = WindoxLocalOperation()
            elif platform.system() == "Linux":
                self.__system_operation = LinuxLocalOperation()
        else:
            self.system_operation = LinuxRemoteOperation(remote_mock_server_machine)

        mock_server_listen_port = mock_server_port
        mock_server_ip = self.__remote_mock_server_machine["ip"] if self.__remote_mock_server_machine else "127.0.0.1"
        self.__query_request_data_interface_url = f"http://{mock_server_ip}:{mock_server_listen_port}/get_mock_server_all_request_data"
        self.__clear_request_data_interface_url = f"http://{mock_server_ip}:{mock_server_listen_port}/clear_mock_server_request_data"

    def add_route(self,route_path,response_date="{}",response_status='200',response_headers='{}',processing_time = '0'):
        """
        :param route_path:    字符串类型,模拟接口的请求路径
        :param response_date:  字符串类型,模拟接口的响应数据
        :param response_status: 字符串类型,响应状态码
        :param response_headers: 字符串类型，字符串里的内容是一个字典 比如 '{"test_key":"test_value"}',模拟服务的响应头
        :param processing_time: 字符串类型,指模拟服务器 特意 sleep 固定的时间，再返回数据
        :return:
        """

        route_path = route_path.replace("mock_other_path","<path:path>")
        get_request_data_code= '{"request_url": request_url, "request_method": request_method, "request_body": request_body,"request_headers": request_headers}'
        route_code_list_len = len(self.__route_code_list)

        route_code = f"""@app.route('{route_path}',methods=["POST","GET","PURGE"])
def processing_requests_{route_code_list_len}(**args):
    request_method = request.method
    request_url = request.url
    request_headers = dict(request.headers)
    request_body = request.data.decode(encoding="UTF-8")

    request_data = {get_request_data_code}
    all_request_data_list.append(request_data)

    sleep_time = {processing_time}
    sleep(sleep_time)

    response_date = '''{response_date}'''
    response_status = {response_status}
    response_headers = {response_headers}

    resp = make_response(response_date,response_status)
    for key, values in response_headers.items():
        resp.headers[key] = values

    return resp
    """

        self.__route_code_list.append(route_code)

    #立刻启动模拟服务
    def start_mock_server(self):
        route_code_string = "\n".join(self.__route_code_list)
        flask_code = f"""
from flask import request,app,Flask,make_response,jsonify
import logging
import json
from time import sleep

app=Flask(__name__)
all_request_data_list = []
{route_code_string}

@app.route('/get_mock_server_all_request_data')
def get_mock_server_all_request_data():
    return jsonify(all_request_data_list)

@app.route('/clear_mock_server_request_data')
def clear_mock_server_request_data():
    all_request_data_list.clear()

if __name__=="__main__":
        app.run(host='0.0.0.0',port={self.__mock_server_port})
        """
        with open("mock_server_code.py","w") as fp:
            fp.write(flask_code)

        self.__system_operation.start_mock_server(self.__mock_server_port)
        sleep(4)

    #此函数用于,启动模拟服务之前,先把特定端口号的进程kill调
    def stop_mock_server(self):
        self.__system_operation.stop_mock_server(self.mock_server_port)


    #返回 模拟服务接收到的请求日志
    def get_mock_server_request_data_list(self):
        class MockServerRequestData:
            """
             模拟服务接收日志类,用于方便查询接收日志

             MockServerRequestData类有四个属性解释如下:

             request_url: 字符串类型，请求的uri
             request_method: 字符类型，请求的http方法
             request_body: 字符类型，请求的body
             request_headers: 字典类型，http请求头

            """
            def __init__(self, request_data_dict):
                self.request_url = request_data_dict["request_url"]
                self.request_method = request_data_dict["request_method"]
                self.request_body = request_data_dict["request_body"]
                self.request_headers = request_data_dict["request_headers"]

        mock_server_request_data_list = []

        mock_server_request_data_json = requests.get(self.__query_request_data_interface_url).json()
        for request_data in  mock_server_request_data_json:
            mock_server_request_data = MockServerRequestData(request_data)
            mock_server_request_data_list.append(mock_server_request_data)
        return mock_server_request_data_list

    @property
    def mock_server_request_data_len(self):
        mock_server_request_data_json = requests.get(self.__query_request_data_interface_url).json()
        return len(mock_server_request_data_json)


    def clear_mock_server_request_data(self):
        requests.get(self.__clear_request_data_interface_url)




if __name__ == "__main__":
    mockserver = MockServerClass(mock_server_port=82)
    mockserver.add_route(route_path="/login", response_status='200', response_headers='{"test_key":"test_value"}',
                         response_date='{"Whether login succeeded":true}')
    mockserver.start_mock_server()

    requests.post("http://127.0.0.1:82/login",json={"test2":"test2"})
    requests.post("http://127.0.0.1:82/login", json={"test2": "test2"})






