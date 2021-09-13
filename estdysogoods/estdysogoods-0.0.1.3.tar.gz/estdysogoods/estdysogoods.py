import socket
import time
from iqoptionapi.stable_api import IQ_Option
from sklearn import tree

def edsg_server_data(IP,PORT,NUMBERCONNECT):
	servers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servers.bind((IP,PORT))
	servers.listen(NUMBERCONNECT)

	while True:
	    clientsocket, address = servers.accept()
	    print(f"Connect:{address}:OK")

	    msg = "Connect Success!"
	    clientsocket.send(bytes(msg,"utf-8"))

	    while True:
	        msg = input("SERVER: ")
	        msg = msg
	        clientsocket.send(bytes(msg,"utf-8"))
def edsg_send_data_order_binary(API):
	while True:
		ID_ORDER,CURRENCY_ORDER,TYPE_ORDER,AMOUNT_ORDER,START_ORDER,END_ORDER,RTTIME_ORDER = API.edsg_get_option_open_by_other_pc()
		if ID_ORDER != None:
			API.del_option_open_by_other_pc(ID_ORDER)
			return [AMOUNT_ORDER,CURRENCY_ORDER,TYPE_ORDER,RTTIME_ORDER]
def edsg_receive_data(servers):
    while True:
        data_text = ''
        new_msg = True
        while True:
            msg = servers.recv(9999)
            if new_msg:
                new_msg = False
            data_text += msg.decode("utf-8")
            return data_text
def edsg_main_copytrade_user_binary(useriq,passiq,iphost,port):
	API = IQ_Option(useriq,passiq)
	API.connect()
	servers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servers.connect((iphost, port))
	data_id1 = []
	data_id2 = []
	while True:
		data_order = edsg_receive_data(servers)
		data_id1 = [data_order]
		if str(data_id1[0]) == "Connect Success!":
			print("Connect Success!")
		if data_id1 != data_id2 and str(data_id1[0]) != "Connect Success!":
			res = (data_order.strip('][').split(', '))
			ID_ORDER       = int(res[0].strip("']['"))
			CURRENCY_ORDER = res[1]
			TYPE_ORDER	   = res[2]
			AMOUNT_ORDER   = res[3]
			RTTIME_ORDER   = res[-1]
			data_id2 = [ID_ORDER]
			API.buy(AMOUNT_ORDER,CURRENCY_ORDER.strip("''"),TYPE_ORDER.strip("''"),int(RTTIME_ORDER)-int(1))
def edsg_main_copytrade_master_binary(ip,port,numberconnect,useriq,passiq):
	servers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servers.bind((socket.gethostname() ,port))
	servers.listen(numberconnect)
	API = IQ_Option(useriq,passiq)
	API.connect()
	while True:
		master = edsg_server_data(servers,API)
def edsg_send_order_pc(API):
	print("OK")
	while True:
		ID_ORDER,CURRENCY_ORDER,TYPE_ORDER,AMOUNT_ORDER,START_ORDER,END_ORDER,RTTIME_ORDER = API.edsg_get_option_open_by_other_pc()
		if ID_ORDER != None:
			API.del_option_open_by_other_pc(ID_ORDER)
			return [ID_ORDER,CURRENCY_ORDER,TYPE_ORDER,AMOUNT_ORDER,RTTIME_ORDER]
def edsg_server_data(servers,API):

	clientsocket, address = servers.accept()
	print("Connect ip:",address[0],"Port",address[1],"OK")

	msg_wc = "Connect Success!"
	clientsocket.send(bytes(msg_wc,"utf-8"))
	while True:
	     msg = str(edsg_send_order_pc(API))
	     msg = msg
	     clientsocket.send(bytes(msg,"utf-8"))
"""def ip(ip,port,numberconnect):
	servers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servers.bind((ip,port))
	servers.listen(numberconnect)
	return servers"""
def edsg_main_master_copytrade_binary(port,numberconnect,useriq,passiq):
	servers = ip(port,numberconnect)
	API = IQ_Option(useriq,passiq)
	API.connect()
	while True:
		edsg_send_order_pc2 = edsg_server_data(servers,API)
def edsg_basic_test_tree_dl(data_one,data_two,rs):
    tree_dl = tree.DecisionTreeClassifier()
    tree_dl = tree_dl.fit(data_one,data_two)
    return tree_dl.predict([rs])
def edsg_get_indicator_BBANDS_Bollinger_Bands(close,input_timeperiod,input_Deviation):
    upperband, middleband, lowerband = BBANDS(close, timeperiod=input_timeperiod, nbdevup=input_Deviation, nbdevdn=input_Deviation, matype=0)
    return upperband, middleband, lowerband
def edsg_get_indicator_Double_Exponential_Moving_Average(close,input_timeperiod):
    INDY_DEMA = DEMA(close, timeperiod=input_timeperiod)
    return INDY_DEMA