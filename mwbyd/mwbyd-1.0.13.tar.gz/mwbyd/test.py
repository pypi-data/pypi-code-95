# *__coding: UTF-8__*
import socket
import uuid

class ABC():

	def name(self,name=''):
		print(name)
		return name
	
	
def getinfo():
    myip=socket.gethostbyname(socket.gethostname())
    print("本机IP地址是：:"+myip)
    node=uuid.getnode()
    mac=uuid.UUID(int=node).hex[-12:]
    print("本机Mac地址是："+mac)

def hello():
    return ("mwbyd欢迎你!!!")

if __name__ == '__main__':
    getinfo()
