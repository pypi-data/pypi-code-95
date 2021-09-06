from sync_ import User 
from sync_.authorization import Account
from jwt_upd import JWtoken
import datetime
# Авторизация
# account = Account(email='kmoloz@mail.ru', password='n21k8o').auth()
# print(account)
# ---

# Продление токена
# jwttt = JWtoken(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoia21vbG96QG1haWwucnUiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zdXJuYW1lIjoi0KLQvtC60LzQsNC60L7QsiDQnS7Qny4iLCJuYmYiOjE2MzA0NTE3NjgsImV4cCI6MTYzMTA1NjU2OCwiaXNzIjoiVmVkS2FmIiwiYXVkIjoiTU1JU0xhYiJ9.FfKRQDlar8RiyESSB_UEcCtaQSRy3T1VDMZ9lzKM9qY")
# updToken = jwttt.decoded()
# print(updToken)
# ---


token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoia21vbG96QG1haWwucnUiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zdXJuYW1lIjoiXHUwNDIyXHUwNDNlXHUwNDNhXHUwNDNjXHUwNDMwXHUwNDNhXHUwNDNlXHUwNDMyIFx1MDQxZC5cdTA0MWYuIiwibmJmIjoxNjMwNDUxNzY4LCJleHAiOjE4MzEwNTY1NjgsImlzcyI6IlZlZEthZiIsImF1ZCI6Ik1NSVNMYWIifQ.ajwp2bxcazBRQY030TcydTjg1rQIKjCTxMAivFco6jU"
user = User(token)
# print(user.infoStudent(studentID = -16370))
# for i in user.infoRasp(groupID = 1565)["data"]["rasp"]:
	# print(i)
# 	print(
# f"""Пара состоится: {i["день_недели"]}
# Время пары: {i["начало"]} - {i["конец"]}
# Название предмета: "{i["дисциплина"]}"
# Аудитория: {i["аудитория"]}
# Преподаватель: {i["преподаватель"]}"""
# 		)
	# print()

calendar = {
	"января":"01",
	"февраля":"02",
	"марта":"03",
	"апреля":"04",
	"мая":"05",
	"июня":"06",
	"июля":"07",
	"августа":"08",
	"сентября":"09",
	"октября":"10",
	"ноября":"11",
	"декабря":"12"
}
def raspDay(groupID, nameday = None, weekday = None):
	now = datetime.datetime.now()
	sdate = now.strftime("%Y-%m-%d")

	if nameday is not None:
		if nameday.lower() == "завтра":
			date_deadline = now + datetime.timedelta(days=1)
		elif nameday.lower() == "после завтра":
			date_deadline = now + datetime.timedelta(days=2)
		else:
			nameday = nameday.split(" ")
			s = datetime.datetime.strptime(f"{nameday[0]}.{calendar[nameday[1]]}.{now.year}", '%d.%m.%Y')
			sdate = s.strftime("%Y-%m-%d")
			nameday = s.strftime("%Y-%m-%dT%H:%M:%S")


	pars = user.infoRasp(groupID = groupID, sdate=sdate)["data"]["rasp"]
	# print(nameday)
	rasp_arr = []
	sdate = datetime.datetime.strptime(sdate, '%Y-%m-%d').strftime("%Y-%m-%dT%H:%M:%S")
	for par in pars:
		if (nameday is not None and nameday in par["дата"]) or (sdate in par["дата"]):
			text_rasp = f"""{par["номерЗанятия"]} пара ({par["начало"]} - {par["конец"]}):
Название предмета: "{par["дисциплина"]}"
Аудитория: {par["аудитория"]}
Преподаватель: {par["преподаватель"]}"""
			rasp_arr.append(text_rasp)

	# print(rasp_arr)
	# состоится: {par["день_недели"]}

	print("\n\n".join(rasp_arr))

raspDay(groupID =1565, nameday="6 сентября")

# to = datetime.datetime.strptime(par["дата"], "%Y-%m-%dT%H:%M:%S").date()
# for_ = to.strftime("%d.%m")
# print(to)
# print(for_)
