import requests
from gitamite import glearn, moodle

class Moodle:
    s = requests.session()
    username = 'username_here'
    password = 'password_here'

    def isMoodleLoggedIn(self):
        return moodle.isMoodleLoggedIn(self)

    def getMoodleHomepage(self):
        return moodle.getMoodleHomepage(self)

    def loginMoodle(self):
        moodle.loginMoodle(self)

    def logoutMoodle(self):
        moodle.logoutMoodle(self)

    def getUpcomingActivities(self):
        return moodle.getUpcomingActivities(self)

class Glearn:

    s = requests.session()
    username = 'username_here'
    password = 'password_here'

    def isGlearnLoggedIn(self):
        return glearn.isGlearnLoggedIn(self)

    def loginGlearn(self):
        glearn.loginGlearn(self)

    def getGlearnHomePage(self):
        return glearn.getGlearnHomePage(self)

    def getPendingAssignments(self):
        return glearn.getPendingAssignments(self)
        
    def getTimetable(self):
        return glearn.getTimetable(self)
    
    def getTimetableToday(self):
        return glearn.getTimetableToday(self)
    
    def getCourses(self):
        return glearn.getCourses(self)

    def codeToName(self, timetable):
        return glearn.codeToName(self, timetable)