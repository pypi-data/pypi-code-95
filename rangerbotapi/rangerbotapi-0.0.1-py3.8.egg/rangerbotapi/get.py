import requests 
import html2text
def getuserinfo(id):
	"""
	user info lekerdezese
	"""
	url= "https://rangerbot.hu/lekeres/user/?id="
	
	response = requests.get(url + id)
	html= response.text
	print(html2text.html2text(html))
	
def getserverinfo(serverid):
	"""
	szerver info lekerdezes
	"""
	url= "https://rangerbot.hu/lekeres/guild/?id="
	
	response= requests.get(url + serverid)
	html= response.text
	print(html2text.html2text(html))
	
