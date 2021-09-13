from datetime import datetime
import requests
from gitamite import helper

def isGlearnLoggedIn(self):
    response1 = requests.get("https://gstudent.gitam.edu/Welcome.aspx").text
    response2 = self.s.get("https://gstudent.gitam.edu/Welcome.aspx").text
    return not helper.soupify(response1).find('title').text == soupify(response2).find('title').text

def loginGlearn(self):
    source = self.s.get("https://login.gitam.edu/Login.aspx").text
    response = self.s.post("https://login.gitam.edu/Login.aspx", glearnFormData(source, self.username, self.password))
    if helper.isWrongGlearn(response.text):
        print("Wrong Credentials")

def getGlearnHomePage(self):
    response = self.s.get('https://gstudent.gitam.edu/G-Learn.aspx')
    return response.text

def getPendingAssignments(self):
    response = self.getGlearnHomePage()
    soup = soupify(response)
    r = soup.find(id='ContentPlaceHolder1_GridView1')
    ar=[]
    for i in r.find_all('td'):
        ar.append(str(i.text).strip().split('\n'))
    return ar

def getTimetable(self):
    response = self.s.get("https://gstudent.gitam.edu/Newtimetable.aspx").text
    table = helper.soupify(response).find(id='MainContent_grd1')
    rows = table.find_all('tr')
    timetable = []
    for tr in rows:
        cells = tr.find_all(['td', 'th'])
        temp = []
        for cell in cells:
            temp.append(cell.text)
        timetable.append(temp)
    return timetable

def getTimetableToday(self):
    timetable = self.getTimetable()
    day = datetime.now().weekday()+1
    if day > len(timetable):
        return None
    return timetable[0],timetable[day]

def getCourses(self):
    response = self.s.get("https://gstudent.gitam.edu/G-Learn.aspx").text
    table = helper.soupify(response).find(id='ContentPlaceHolder1_GridView2')
    cells = table.find_all('td')
    subjectcodes = []
    for cell in cells:
        subjectcodes.append(cell.text.strip().split('\n'))
    return subjectcodes

def codeToName(self, timetable):
    courses = getCourses(self)
    for course in courses:
        code = course[0]
        name = course[1]
        for day in timetable:
            for subject in day:
                if code in subject:
                    day[day.index(subject)] = name
    return timetable
