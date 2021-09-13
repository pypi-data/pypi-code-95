import requests
from gitamite import helper


def isMoodleLoggedIn(self):
    response1 = requests.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
    response2 = self.s.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
    return not helper.soupify(response1.text).find('title').text == helper.soupify(response2.text).find('title').text

def getMoodleHomepage(self):
    response = self.s.get('https://learn.gitam.edu/my/')
    return response.text

def loginMoodle(self):
    response1 = self.s.get("https://learn.gitam.edu/login/index.php")
    response2 = self.s.post("https://learn.gitam.edu/login/index.php",helper.moodleFormData(response1.text, self.username, self.password))
    if helper.isWrongMoodle(response2.text):
        print("Wrong Credentials.")

def logoutMoodle(self):
    response = self.s.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
    soup = helper.soupify(response.text)
    logoutLink = soup.find('a', {'aria-labelledby': 'actionmenuaction-6'})['href']
    self.s.get(logoutLink)

def getUpcomingActivities(self):
    response = self.s.get("https://learn.gitam.edu/calendar/view.php?view=upcoming")
    tup = []
    soup = helper.soupify(response.text)
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
