import requests
from datetime import datetime
from  helper import *

class Moodle:
    s = requests.session()
    username = 'username_here'
    password = 'password_here'

    def isMoodleLoggedIn(self):
        response1 = requests.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
        response2 = self.s.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
        return not soupify(response1.text).find('title').text == soupify(response2.text).find('title').text

    def getMoodleHomepage(self):
        response = self.s.get('https://learn.gitam.edu/my/')
        return response.text

    def loginMoodle(self):
        response1 = self.s.get("https://learn.gitam.edu/login/index.php")
        response2 = self.s.post("https://learn.gitam.edu/login/index.php",
                                moodleFormData(response1.text, self.username, self.password))
        if isWrongMoodle(response2.text):
            print("Wrong Credentials.")

    def logoutMoodle(self):
        response = self.s.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
        soup = soupify(response.text)
        logoutLink = soup.find('a', {'aria-labelledby': 'actionmenuaction-6'})['href']
        self.s.get(logoutLink)

    def getUpcomingActivities(self):
        response = self.s.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
        tup = []
        soup = soupify(response.text)
        for i in soup.findAll('div', {'class': 'event m-t-1'}):
            activity = i.find('h3', {'class': 'name d-inline-block'}).text
            time = i.find('div', {'class': 'col-11'}).text
            link = ''
            try:
                link = i.find('div', {'class': 'description-content col-11'}).find('a')['href']
            except:
                pass
            tup.append((activity, time, link))
        return tup

class Glearn:

    s = requests.session()
    username = 'username_here'
    password = 'password_here'

    def isGlearnLoggedIn(self):
        response1 = requests.get("https://gstudent.gitam.edu/Welcome.aspx").text
        response2 = self.s.get("https://gstudent.gitam.edu/Welcome.aspx").text
        return not soupify(response1).find('title').text == soupify(response2).find('title').text

    def loginGlearn(self):
        source = self.s.get("https://login.gitam.edu/Login.aspx").text
        response = self.s.post("https://login.gitam.edu/Login.aspx", glearnFormData(source, self.username, self.password))
        if isWrongGlearn(response.text):
            print("Wrong Credentials")

    def getTimetable(self):
        response = self.s.get("https://gstudent.gitam.edu/Newtimetable.aspx").text
        response1 = self.s.get("https://gstudent.gitam.edu/G-Learn.aspx").text
        v = soupify(response).find(id='MainContent_grd1')
        x = soupify(response1).find(id='ContentPlaceHolder1_GridView2')
        timings = []
        classes = []
        subjectCodes = []
        for i in x.findAll('td'):
            subjectCodes.append((i.find('h4').text, i.find('h6').text))
        for i in v.findAll('tr'):
            if 'th' in str(i):
                for j in i.findAll('th'):
                    timings.append(j.text)
            if 'td' in str(i):
                eachDay = []
                for j in i.findAll('td'):
                    y = j.text
                    for k in subjectCodes:
                        if k[0] in j.text:
                            y = k[1]
                            break
                    eachDay.append(y)
                classes.append(eachDay)
        return timings, classes

    def getTimetableToday(self):
        weekday, classes = self.getTimetable()
        now = datetime.now()
        if now.weekday() > 4:
            return None
        lst = []
        nextclass = ()
        for i in range(len(weekday)):
            if classes[now.weekday()][i] != '':
                lst.append((convertTo12Hour(weekday[i]), classes[now.weekday()][i]))
                if not weekday[i] == 'WEEKDAY':
                    hour = int(weekday[i].split("to")[0].split(':')[0])
                    if len(weekday) > 1 and now.hour < hour and nextclass == ():
                        nextclass = convertTo12Hour(weekday[1]), classes[now.weekday()][0]
                    elif hour == now.hour and now.minute < 15:
                        nextclass = convertTo12Hour(weekday[i]), classes[now.weekday()][i]
                    elif hour == now.hour and now.minute >= 15 and i + 1 < len(weekday):
                        nextclass = convertTo12Hour(weekday[i + 1]), classes[now.weekday()][i + 1]

        return nextclass, lst[1:]