import requests
import json
import datetime

# Получаем токен от аккаунта и наслаждаемся
class User:


	"""
	METHODS_URL = {

		/GET/
		Авторизация: https://edu-tpi.donstu.ru/Account/Login.aspx
		Все сообщения: https://edu-tpi.donstu.ru/api/Mail/InboxMail
		Непрочитанные сообщения: https://edu-tpi.donstu.ru/api/Mail/CheckMail
		Конкретное сообщение: https://edu-tpi.donstu.ru/api/Mail/InboxMail?&id={id}
		Просмотр студентов в группе: https://edu-tpi.donstu.ru/api/Mail/Find/Students?groupID={groupID}
		Поиск студента по ФИО: https://edu-tpi.donstu.ru/api/Mail/Find/Students?fio={fio}
		Поиск преподователя по ФИО: https://edu-tpi.donstu.ru/api/Mail/Find/Prepods?fio={fio}
		Список всех групп в {N-N} учебном году: https://edu-tpi.donstu.ru/api/groups?year={N1}-{N2}
		Информация об аккаунте: https://edu-tpi.donstu.ru/api/tokenauth
		Информация о студенте: https://edu-tpi.donstu.ru/api/UserInfo/Student?studentID=-{studentID}
		Возвращает максимульный/минимальный/текущий день расписания группы GROUP: https://edu-tpi.donstu.ru/api/GetRaspDates?idGroup=GROUP 
		Возвращает расписание группы GROUP с DATE: https://edu-tpi.donstu.ru/api/Rasp?idGroup=GROUP&sdate=DATE

		/POST/
		Отправить сообщение на почту: https://edu-tpi.donstu.ru/api/Mail/InboxMail


	}
	"""

	def __init__(self, token):
		self.authToken = "Bearer {}".format(token)
		self.url_api = "https://edu-tpi.donstu.ru/api/"
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 YaBrowser/21.3.3.234 Yowser/2.5 Safari/537.36",
			"authorization": self.authToken,
			"Content-Type": "application/json; charset=utf-8"
		}

	def checking_unread_messages(self):
		return requests.get(f"{self.url_api}Mail/CheckMail", headers=self.headers).json()

	def checking_all_mail(self, page: int = 1):
		return requests.get(f"{self.url_api}Mail/InboxMail?page=1&pageEl=15&unreadMessages=false&searchQuery=", headers=self.headers).json()

	def read_mail_message(self, messageID):
		for msg in self.checking_all_mail()['data']['messages']:
			if msg['messageID'] == messageID:
				return requests.get(f"{self.url_api}Mail/InboxMail?id={msg['id']}", headers=self.headers).json()['data']['messages'][0]

	def find_stundent(self, fio):
		return requests.get(f"{self.url_api}Mail/Find/Students?fio={fio}", headers=self.headers).json()


	def find_teacher(self, fio):
		return requests.get(f"{self.url_api}Mail/Find/Prepods?fio={fio}", headers=self.headers).json()

	def all_groups_year(self, year: int = datetime.datetime.now().year):
		return requests.get(f"{self.url_api}groups?year={year}-{year+1}").json()

	def send_message(self, statusID, from_user, title_message, text_message, type_message: int = 1):

		if statusID == 0:
			usertoID = self.find_stundent(fio=from_user)['data']['arrStud']
		elif statusID == 1:
			usertoID = self.find_teacher(fio=from_user)['data']['arrPrep']
		elif statusID == 2:
			pass

		print(usertoID)
		data = {
			"markdownMessage": text_message,
			"htmlMessage": "",
			"message": "",
			"theme": title_message,
			"userToID": usertoID,
			"typeID": type_message,
		}
		req = requests.post(f"{self.url_api}Mail/InboxMail", data=json.dumps(data), headers=self.headers)

	def infoAccount(self):
		return requests.get(f"{self.url_api}tokenauth", headers=self.headers).json()

	def infoStudent(self, studentID):
		return requests.get(f"{self.url_api}UserInfo/Student?studentID={studentID}", headers=self.headers).json()

	def infoRasp(self, groupID, sdate = datetime.datetime.now().strftime("%Y-%m-%d")):
		return requests.get(f"{self.url_api}Rasp?idGroup={groupID}&sdate={sdate}", headers=self.headers).json()

class Account:

	def __init__(self, email, password):
		self.email = email
		self.password = password
		self.auth_url = 'https://edu-tpi.donstu.ru/Account/Login.aspx'

		self.data = {
			"__VIEWSTATE": "/wEPDwULLTE5Njc0MjQ0ODAPZBYCZg9kFgICAw9kFggCAQ88KwAKAgAPFgIeDl8hVXNlVmlld1N0YXRlZ2QGD2QQFgFmFgE8KwAMAQAWBh4EVGV4dAUO0JPQu9Cw0LLQvdCw0Y8eC05hdmlnYXRlVXJsBQ5+L0RlZmF1bHQuYXNweB4OUnVudGltZUNyZWF0ZWRnZGQCCw8WAh4JaW5uZXJodG1sBTrQrdC70LXQutGC0YDQvtC90L3QvtC1INC/0L7RgNGC0YTQvtC70LjQviDRgdGC0YPQtNC10L3RgtCwZAINDzwrAAkCAA8WAh8AZ2QGD2QQFgFmFgE8KwALAQAWCh8BZR4ETmFtZQUCZ2gfAmUeBlRhcmdldGUfA2dkZAIRDzwrAAQBAA8WAh4FVmFsdWUFHTIwMjEgwqkgQ29weXJpZ2h0IGJ5IE1NSVMgTGFiZGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgMFD2N0bDAwJEFTUHhNZW51MQURY3RsMDAkQVNQeE5hdkJhcjEFKmN0bDAwJE1haW5Db250ZW50JHVjTG9naW5Gb3JtUGFnZSRidG5Mb2dpbj6AgDxOZVnZwij5bL/VFy59O/phPxVn2KrrW7LSWHWF", "ctl00$MainContent$ucLoginFormPage$btnLogin": "(unable to decode value)",

			"ctl00$MainContent$ucLoginFormPage$tbUserName$State": "{&quot;rawValue&quot;:&quot;"+self.email+"&quot;,&quot;validationState&quot;:&quot;&quot;}",
			"ctl00$MainContent$ucLoginFormPage$tbPassword$State": "{&quot;rawValue&quot;:&quot;"+self.password+"&quot;,&quot;validationState&quot;:&quot;&quot;}",
			"ctl00$MainContent$ucLoginFormPage$tbUserName": self.email,
			"ctl00$MainContent$ucLoginFormPage$tbPassword": self.password, 
		}


	def auth(self):
		s = requests.Session()
		req = s.post(self.auth_url, data=self.data)
		try:
			if s.cookies.items()[2][1]: 
				authToken = s.cookies.items()[2][1]
				s.cookies.clear()
				return authToken
			else: return False
		except IndexError as e:				
			return False