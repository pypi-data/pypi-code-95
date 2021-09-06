from bs4 import BeautifulSoup

def isWrongMoodle(text):
    return "Invalid login" in text

def isWrongGlearn(text):
    return "Invalid" in text

def glearnFormData(htmlsource, username, password):
    soup = soupify(htmlsource)
    viewstate = soup.find(id="__VIEWSTATE")['value']
    viewstategenerator = soup.find(id="__VIEWSTATEGENERATOR")['value']
    eventvalidation = soup.find(id="__EVENTVALIDATION")['value']
    requestBody = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        "txtusername": username,
        "password": password,
        "Submit": "Login"
    }
    return requestBody

def soupify(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup

def convertTo12Hour(text):
    try:
        hour = int(text.split("to")[0].split(':')[0])
        if hour > 12:
            hour = hour - 12
        x = text
        x = "{}:{} to {}:{}".format(hour, x.split('to')[0].split(':')[1], hour, x.split('to')[1].split(':')[1])
        return x
    except:
        return text

def moodleFormData(htmlsource, username, password):
    soup = soupify(htmlsource)
    logintoken = soup.find("input", {"name": "logintoken"})['value']
    requestBody = {
        "logintoken": logintoken,
        "username": username,
        "password": password
    }
    return requestBody
