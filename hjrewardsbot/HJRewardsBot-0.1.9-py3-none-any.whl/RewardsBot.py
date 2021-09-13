
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import sys
import stdiomask
import os
import pickle
import urllib.parse
import random
import requests
from datetime import date, timedelta, datetime
import json
import time
import os
from datetime import datetime
import errno
import hashlib 
BOTVERSION="0.1.9"
PC_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'
MOBILE_USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0. 3945.79 Mobile Safari/537.36'

LANG="EN" 
GEO = "US"  
TZ = "-5"

AccountName=""
chromePath=""


# Define user-agents
PC_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'
MOBILE_USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0. 3945.79 Mobile Safari/537.36'

def reportTimeout(locatoin:str,ReportingP:str):
    try:
      filename = datetime.now().strftime('%Y-%m-%d')+".txt"
      with open(os.path.join(ReportingP, filename), 'a+') as d:
           d.writelines(['Bot TimeOut Error  unexpected error closed at '+locatoin+' !\n'])
           
    except Exception as e:
        print(e)
def reportDeparture(ReportingP:str,startingPoints: int,POINTS_COUNTER: int):
    try:
      filename = datetime.now().strftime('%Y-%m-%d')+".txt"
      with open(os.path.join(ReportingP, filename), 'a+') as d:
           d.writelines(['[POINTS] You have earned ' +
                  str(POINTS_COUNTER - startingPoints) + ' points today !','[POINTS] You are now at ' +
                  str(POINTS_COUNTER) + ' points !\n'])
           
    except Exception as e:
        print(e)
def reportDailySet(ReportingP:str,DAILYPOINTSREPORTING:str,DAILYTOTALPOINTS:int):
    try:
      filename = datetime.now().strftime('%Y-%m-%d')+".txt"
 
      with open(os.path.join(ReportingP, filename), 'a+') as d:
           DAILYPOINTSREPORTING+=["completed Daily Tasks Successfully with Total "+str(DAILYTOTALPOINTS)+" Points \n"]
           d.writelines(DAILYPOINTSREPORTING)
        
    except Exception as e:
        print(e)

def reportPromotionsSet(ReportingP:str,PROMOTIONREPOTING:str,PROMOTIONPOINTS:int):
    try:
      filename = datetime.now().strftime('%Y-%m-%d')+".txt"
    
      with open(os.path.join(ReportingP, filename), 'a+') as d:
           PROMOTIONREPOTING+=["completed Promotions Tasks Successfully with Total "+str( PROMOTIONPOINTS)+" Points \n"]
           d.writelines(PROMOTIONREPOTING)
           
    except Exception as e:
        print(e)




def generateDailyReport(ReportingP:str,AccountemailAddress:str):
    try:
      filename = datetime.now().strftime('%Y-%m-%d')+".txt"
      
      print("Account : "+AccountemailAddress+" \n","started at : "+datetime.now().strftime('%H:%M:%S'))
      print("developed by : Hassan jlilati - bot ver: "+BOTVERSION)
      with open(os.path.join(ReportingP, filename), 'a+') as d:
           d.writelines(["\n \n  Account : "+AccountemailAddress+" \n","started at : "+datetime.now().strftime('%H:%M:%S')+" \n"])
    except Exception as e:
        print(e)


 

def reportSearchSet(ReportingP:str,SEARCHREPORTING:str,SEARCHTOTALPOINTS:int):
    try:
      filename = datetime.now().strftime('%Y-%m-%d')+".txt"
     
      with open(os.path.join(ReportingP, filename), 'a+') as d:
           SEARCHREPORTING+=["completed Search Tasks Successfully with Total "+ str( SEARCHTOTALPOINTS)+" Points \n"]
           d.writelines(SEARCHREPORTING)
          
    except Exception as e:
        print(e)
def delay():
    time.sleep(random.randint(2, 3))

# Define function to check if config.pickle is empty or not


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


# Define function to input email and password onto config.pickle using pickle lib
def inputCredentials():
    # (input('[INPUT] Enter the number of accounts in your Microsoft Family: '))
    Accounts = "1"
    numberAccounts = 1  # int(Accounts)
    if numberAccounts > 5:
        print('[IP LIMIT] MS Family only allows 5 accounts per IP.')
        inputCredentials()
    else:
        mydict = email_password(numberAccounts)
        with open('config.pickle', 'wb') as handle:
            pickle.dump(mydict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # Load data (deserialize)
        with open('config.pickle', 'rb') as handle:
            unserialized_data = pickle.load(handle)

        print(mydict == unserialized_data)

    displayCredentials()

# Define display credentials


def waitUntilpanelshow(browser: WebDriver):
    try:
        element = WebDriverWait(browser, 10).until(
        ec.presence_of_element_located((By.ID, "overlayPanel"))
        )
        return True
    except:
        return False
 

def displayCredentials():
    # Open config.pickle to unpickle email and password and send to login function
    with open('config.pickle', 'rb') as handle:
        b = pickle.load(handle)
        # print (b)

    key_iterable = b.keys()
    key_list = list(key_iterable)
    # print(key_list)

    item_iterable = b.values()
    item_list = list(item_iterable)
    # print(item_list)

    return key_list, item_list


def email_password(numberAccounts: int, AccountemailAddress:str,Accountpassword:str ):
    mydict = dict()
    i = 1
    while i <= numberAccounts:
        print('[INPUT] Rewards account '+str(i))
        email = AccountemailAddress  # input("Enter email address: ")
        email = email.strip()
        if email == '':
            break
        # password = input("Password: ")
        password = Accountpassword  # stdiomask.getpass('Enter password: ')
        password = password.strip()
        mydict[email] = password
        # print(mydict)
        i += 1

    return mydict

# Define browser setup function


def browserSetup(Chrome_path:str,headless_mode: bool = False, user_agent: str = PC_USER_AGENT) -> WebDriver:
    # Create Chrome browser




    from selenium.webdriver.chrome.options import Options
    options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2,"profile.default_content_settings.geolocation":2}
    
    options.add_experimental_option("prefs", prefs)
    
    options.add_argument("user-agent=" + user_agent)
    options.add_argument('lang=' + LANG.split("-")[0])
    if headless_mode:
        options.add_argument("--headless")
    options.add_argument('log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    global chromePath
    chromePath=Chrome_path

    chrome_browser_obj = webdriver.Chrome(executable_path=os.path.basename(Chrome_path), options=options)
    #chrome_browser_obj.set_network_conditions(
    #offline=False,
    #latency=500,  # additional latency (ms)
    #download_throughput=1024*0.5 ,  # maximal throughput
    #upload_throughput=1024*0.5)
    return chrome_browser_obj

# Define login function


def login(browser: WebDriver, email: str, pwd: str, POINTS_COUNTER:int,PorgramTimeOut,ReportingP,isMobile: bool = False):
    # Access to bing.com

  try:  
    if time.time() > PorgramTimeOut:reportTimeout("login",ReportingP), exit()
    #validateUser(email,ReportingP)



    browser.get('https://login.live.com/')
    # Wait complete loading
    waitUntilVisible(browser, By.ID, 'loginHeader', 10)
    
    # Enter email
    print('[LOGIN]', 'Writing email...')
    waitUntilVisible(browser,By.NAME,"loginfmt")
    browser.find_element_by_name("loginfmt").send_keys(email)
    # Click next
    try:
       browser.find_element_by_id('idSIButton9').click()
    except:
        pass
    # Wait 2 seconds
    time.sleep(4)
    # Wait complete loading
    waitUntilVisible(browser, By.ID, 'loginHeader', 10)
    # Enter password
    # browser.find_element_by_id("i0118").send_keys(pwd)
    waitUntilVisible(browser,By.NAME,"passwd")
    browser.execute_script(
        "document.getElementById('i0118').value = '" + pwd + "';")
    print('[LOGIN]', 'Writing password...')
    # Click next
    try:
        browser.find_element_by_id('idSIButton9').click()
    except:
        pass
    # Wait 5 seconds
    time.sleep(5)
    # Click Security Check
    print('[LOGIN]', 'Passing security checks...')
    try:
        browser.find_element_by_id('iLandingViewAction').click()
    except (NoSuchElementException, ElementNotInteractableException) as e:
        pass
    # Wait complete loading
    try:
        waitUntilVisible(browser, By.ID, 'KmsiCheckboxField', 10)
    except (TimeoutException) as e:
        pass
    # Click next
    try:
        browser.find_element_by_id('idSIButton9').click()
        # Wait 5 seconds
        time.sleep(5)
    except (NoSuchElementException, ElementNotInteractableException) as e:
        pass
    print('[LOGIN]', 'Logged-in!')
    # Check Login
    print('[LOGIN]', 'Ensuring login on Bing...')
    time.sleep(4)
    
     
    if(browser.current_url.find("https://account.live.com/Abuse") != -1): 
        handleAccountBlock(email,ReportingP,browser)

    if(browser.current_url.find("https://account.live.com/identity/confirm") != -1): 
        handleidentityconfirm(email,ReportingP,browser)

        
    if not isMobile:
        POINTS_COUNTER= checkBingLogin(browser,POINTS_COUNTER,PorgramTimeOut,ReportingP, isMobile)
    else:
        checkmobileLogin(browser, email, pwd, POINTS_COUNTER,PorgramTimeOut,ReportingP,isMobile)
    return POINTS_COUNTER
  except Exception as e:
     if time.time() > PorgramTimeOut:reportTimeout("login",ReportingP), exit()
     POINTS_COUNTER= login(browser, email, pwd,POINTS_COUNTER,PorgramTimeOut,ReportingP,isMobile)
     return POINTS_COUNTER
def handleAccountBlock(email:str,ReportingP:str,browser:WebDriver):
    reportPath= os.path.dirname(ReportingP)  
    try:
        filename = "suspend.txt"
        with open(os.path.join(reportPath, filename), 'a+') as d:
           d.writelines(['\n\n today is  ' +datetime.now().strftime('%Y-%m-%d')+
           '  Account: ' + email +' has blocked'
                '\n\n'])
        browser.quit()        
        time.sleep(4)        
        global chromePath  
        browserSetup(chromePath,False,PC_USER_AGENT)
        time.sleep(150) 
        exit()
    except Exception as e:
        print(e) 

def handleidentityconfirm(email:str,ReportingP:str,browser:WebDriver):
    reportPath= os.path.dirname(ReportingP)  
    try:
        filename = "suspend.txt"
        with open(os.path.join(reportPath, filename), 'a+') as d:
           d.writelines(['\n\n today is  ' +datetime.now().strftime('%Y-%m-%d')+
           '  Account: ' + email +' has need confirm'
                '\n\n'])
        browser.quit()        
        time.sleep(4)        
        global chromePath  
        browserSetup(chromePath,False,PC_USER_AGENT)
        time.sleep(150) 
        exit()
    except Exception as e:
        print(e) 



def validateUser(email:str,ReportingP:str):
    reportPath= os.path.dirname(ReportingP)  
    try:
        filene = os.path.join(reportPath,  "licence.txt")
        with open(os.path.normpath(filene), 'r+') as d:
           lines = d.readlines()
           if len(lines) == 0:
               print("Subscription has expired please contact Admin hasssanjlilati10000@gmail.com")
               time.sleep(20) 
               exit()
        
        str2hash =  email+"HassanJlilati10000-"+datetime.now().strftime('%Y-%m')
        result = hashlib.md5(str2hash.encode())
        hexpass= result.hexdigest()
        for line in lines:
            Account=line.split(":")[0]
            if Account==email:
                if(line.split(":")[1]==hexpass):
                    return
        print("Subscription has expired please contact Admin hasssanjlilati10000@gmail.com")
        time.sleep(20) 
        exit()
    except Exception as e:
        print(e) 


def checkmobileLogin(browser: WebDriver, email: str, pwd: str, POINTS_COUNTER:int,PorgramTimeOut,ReportingP,isMobile: bool = False):
    if time.time() > PorgramTimeOut:reportTimeout("checkmobileLogin",ReportingP), exit()
    islogin=False
    tries=0
    while islogin is not True and tries<4 :
         try:
          
            browser.execute_script('''window.open("https://www.bing.com/search?q=mybalance","_blank");''') 
            browser.switch_to.window(window_name=browser.window_handles[1])
            time.sleep(5)
            waitUntilVisible(browser, By.XPATH,
                     '//*[@id="mHamburger"]', 10)
            browser.find_element_by_id('mHamburger').click()
            try:
                time.sleep(3)
                waitUntilVisible(browser, By.XPATH,
                     '//*[@id="hb_s"]', 10)
                browser.find_element_by_id('hb_s').click()
                tries+=1
                islogin=False
                browser.close()
                time.sleep(2)
                browser.switch_to.window(window_name=browser.window_handles[0]) 
            except:  
                try:
                    browser.find_element_by_id('hb_n')
                    islogin=True
                    browser.close()
                    time.sleep(2)
                    browser.switch_to.window(window_name=browser.window_handles[0]) 
                except:      
                    islogin=False
                    browser.close()
                    time.sleep(2)
                    browser.switch_to.window(window_name=browser.window_handles[0])   
         except:  
            islogin=False
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])
    

    
          
    if tries > 0:
        browser.get('https://login.live.com/')
        time.sleep(5)
        if(browser.current_url.find("https://account.microsoft.com/") != -1):
           return
        login(browser,email,pwd,POINTS_COUNTER,PorgramTimeOut,ReportingP,isMobile)

         
                  
    

def checkBingLogin(browser: WebDriver, POINTS_COUNTER:int,PorgramTimeOut,ReportingP,isMobile: bool = False):
 
    # Access Bing.com
    if time.time() > PorgramTimeOut:reportTimeout("check bing login",ReportingP), exit()
     
    islogin=False
    tries=0
    while islogin is not True and tries<4 :
         try:
          
            browser.execute_script('''window.open("https://www.bing.com/search?q=mybalance","_blank");''') 
            browser.switch_to.window(window_name=browser.window_handles[1])
            time.sleep(5)
            try:
                time.sleep(8)
                waitUntilVisible(browser, By.NAME,
                     'submit', 15)
                browser.find_element_by_name('submit').click()
                tries+=1
                islogin=False
                browser.close()
                time.sleep(2)
                browser.switch_to.window(window_name=browser.window_handles[0]) 
            except:  
                try:
                    time.sleep(5)
                    browser.find_element_by_id('id_n')
                    islogin=True
                  
                except:      
                    islogin=False
                    browser.close()
                    time.sleep(2)
                    browser.switch_to.window(window_name=browser.window_handles[0])   
         except:  
            islogin=False
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])
    # Wait 8 seconds
    #time.sleep(10)
    # Accept Cookies
    try:
        if not isMobile:
             waitUntilVisible(browser, By.XPATH,
                     '//*[@id="bnp_btn_accept"]', 10)
             browser.find_element_by_id('bnp_btn_accept').click()
             browser.close()
             time.sleep(2)
             browser.switch_to.window(window_name=browser.window_handles[0])
    except:
         browser.close()
         time.sleep(2)
         browser.switch_to.window(window_name=browser.window_handles[0])
    if isMobile:
        try:
            time.sleep(1)
            waitUntilVisible(browser, By.XPATH,
                     '//*[@id="mHamburger"]', 10)
            browser.find_element_by_id('mHamburger').click()
        except:
            try:
                waitUntilVisible(browser, By.XPATH,
                     '//*[@id="bnp_btn_accept"]', 10)
                browser.find_element_by_id('bnp_btn_accept').click()
            except:
                pass
            time.sleep(3)
            try:
                browser.find_element_by_id('mHamburger').click()
            except:
                pass
        try:
            time.sleep(1)
            browser.find_element_by_id('HBSignIn').click()
        except:
            pass
        try:
            time.sleep(2)
            browser.find_element_by_id('iShowSkip').click()
            time.sleep(3)
        except:
            if str(browser.current_url).split('?')[0] == "https://account.live.com/proofs/Add":
                input('[LOGIN] Please complete the Security Check on ' +
                      browser.current_url)
                exit()
    # Wait 2 seconds
    time.sleep(10)
    # Refresh page
    #browser.get('https://bing.com/')
    # Wait 5 seconds
    #time.sleep(10)
    # Update Counter
    try:
        if not isMobile:
            browser.execute_script('''window.open("https://www.bing.com/search?q=mybalance","_blank");''')

            
            browser.switch_to.window(window_name=browser.window_handles[1])
            browser.refresh()
            waitUntilVisible(browser, By.XPATH,
                     '//*[@id="id_rc"]', 10)
            POINTS_COUNTER = int(browser.find_element_by_id(
                'id_rc').get_attribute('innerHTML'))
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])    
            return POINTS_COUNTER   
        else:
            try:
                try:
                    browser.find_element_by_id('bnp_btn_accept').click()
                except:
                    pass
                waitUntilVisible(browser, By.XPATH,
                     '//*[@id="mHamburger"]', 10)
                browser.find_element_by_id('mHamburger').click()
            except:
                pass
                time.sleep(1)
                #browser.find_element_by_id('mHamburger').click()
            time.sleep(1)
            browser.refresh()
            time.sleep(3)
            POINTS_COUNTER = int(browser.find_element_by_id(
                'fly_id_rc').get_attribute('innerHTML'))
            return POINTS_COUNTER    
    except:
       if time.time() > PorgramTimeOut:reportTimeout("chckbing login",ReportingP), exit()
       POINTS_COUNTER= checkBingLogin(browser,POINTS_COUNTER,PorgramTimeOut,ReportingP, isMobile)
       return POINTS_COUNTER    


def waitUntilVisible(browser: WebDriver, by_: By, selector: str, time_to_wait: int = 10):
    WebDriverWait(browser, time_to_wait).until(
        ec.visibility_of_element_located((by_, selector)))


def waitUntilClickable(browser: WebDriver, by_: By, selector: str, time_to_wait: int = 10):
    WebDriverWait(browser, time_to_wait).until(
        ec.element_to_be_clickable((by_, selector)))


def findBetween(s: str, first: str, last: str) -> str:
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def getCCodeLangAndOffset():
    # nfo = #ipapi.location()
    lang = "EN"  # nfo['languages'].split(',')[0]
    geo = "US"  # nfo['country']
    tz = "-5"
    # if nfo['utc_offset'] == None:
    #    tz = str(0)
   # else:
      #  tz = str(round(int(nfo['utc_offset']) / 100 * 60))
    return(lang, geo, tz)


def getGoogleTrends(numberOfwords: int) -> list:
    search_terms = []
    i = 0
    while len(search_terms) < numberOfwords:
        i += 1
        r = requests.get('https://trends.google.com/trends/api/dailytrends?hl=' + LANG + '&ed=' +
                         str((date.today() - timedelta(days=i)).strftime('%Y%m%d')) + '&geo=' + GEO + '&ns=15')
        google_trends = json.loads(r.text[6:])
        for topic in google_trends['default']['trendingSearchesDays'][0]['trendingSearches']:
            search_terms.append(topic['title']['query'].lower())
            for related_topic in topic['relatedQueries']:
                search_terms.append(related_topic['query'].lower())
        search_terms = list(set(search_terms))
    del search_terms[numberOfwords:(len(search_terms)+1)]
    return search_terms


def getRelatedTerms(word: str) -> int:
    r = requests.get('https://api.bing.com/osjson.aspx?query=' +
                     word, headers={'User-agent': PC_USER_AGENT})
    return r.json()[1]


def resetTabs(browser: WebDriver):
    curr = browser.current_window_handle

    for handle in browser.window_handles:
        if handle != curr:
            browser.switch_to.window(handle)
            time.sleep(0.5)
            browser.close()
            time.sleep(0.5)

    browser.switch_to.window(curr)
    time.sleep(0.5)
    browser.get('https://account.microsoft.com/rewards/')


def getAnswerCode(key: str, string: str) -> str:
    t = 0
    for i in range(len(string)):
        t += ord(string[i])
    t += int(key[-2:], 16)
    return str(t)


def bingSearches(browser: WebDriver, numberOfSearches: int,POINTS_COUNTER:int,SEARCHREPORTING:str,SEARCHTOTALPOINTS:int,PorgramTimeOut,ReportingP, isMobile: bool = False):
    if time.time() > PorgramTimeOut:reportTimeout("bing serches",ReportingP), exit() 
    i = 0
    search_terms = getGoogleTrends(numberOfSearches)
    for word in search_terms:
        i += 1
        print('[BING]', str(i) + "/" + str(numberOfSearches))
        points = bingSearch(browser, word, isMobile)
        if points <= POINTS_COUNTER:
            relatedTerms = getRelatedTerms(word)
            for term in relatedTerms:
                points = bingSearch(browser, term, isMobile)
                if not points < POINTS_COUNTER:
                    break

        POINTS_COUNTER = points
        if isMobile == True and i == len(search_terms)-1:
            pass
            # Get_point_total(browser, POINTS_COUNTER)
    SEARCHTOTALPOINTS=0
    SEARCHTOTALPOINTS+=5*numberOfSearches
    if isMobile:
        SEARCHREPORTING+=["done mobile "+str( numberOfSearches) +" search for "+str(SEARCHTOTALPOINTS)+" points \n"]
    else :
        SEARCHREPORTING+=["done desktop "+str( numberOfSearches) +" search for "+str(SEARCHTOTALPOINTS)+" points \n"]
    return SEARCHREPORTING,SEARCHTOTALPOINTS


def bingSearch(browser: WebDriver, word: str, isMobile: bool):
    browser.get('https://bing.com')
    time.sleep(2)
    searchbar = browser.find_element_by_id('sb_form_q')
    searchbar.send_keys(word)
    searchbar.submit()
    time.sleep(random.randint(5, 7))
    points = 0
    try:
        if not isMobile:
            points = int(browser.find_element_by_id(
                'id_rc').get_attribute('innerHTML'))
        else:
            try:
                browser.find_element_by_id('mHamburger').click()
            except UnexpectedAlertPresentException:
                try:
                    browser.switch_to.alert.accept()
                    time.sleep(1)
                    browser.find_element_by_id('mHamburger').click()
                except NoAlertPresentException:
                    pass
            time.sleep(1)
            points = int(browser.find_element_by_id(
                'fly_id_rc').get_attribute('innerHTML'))
    except:
        pass
    return points


def completeDailySetSearch(browser: WebDriver, cardNumber: int,donepoints:int,DAILYTOTALPOINTS:int,DAILYPOINTSREPORTING:str):
    time.sleep(15)
     
    try:
        browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a').click()
        
        DAILYTOTALPOINTS+=donepoints
        DAILYPOINTSREPORTING+=["done daily search for "+str(donepoints)+"  \n"]
    except Exception as e:
        try:
            browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
            DAILYTOTALPOINTS+=donepoints
            DAILYPOINTSREPORTING+=["done daily search for "+str(donepoints)+"  \n"]
        except:   
            pass 
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])

    time.sleep(random.randint(13, 17))
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)
    return DAILYTOTALPOINTS,DAILYPOINTSREPORTING


def completeDailySetSurvey(browser: WebDriver, cardNumber: int,donepoints :int,DAILYTOTALPOINTS:int,DAILYPOINTSREPORTING:str ):
    time.sleep(5)
    try:
        browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a').click()
    except:
        try:
           browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
        except:    
           pass
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(12)
    try:
      browser.find_element_by_id("btoption" + str(random.randint(0, 1))).click()
      time.sleep(10)
      DAILYTOTALPOINTS+=donepoints
      DAILYPOINTSREPORTING+=["done completeDailySetSurvey for "+str(donepoints)+"  \n"]
      return DAILYTOTALPOINTS,DAILYPOINTSREPORTING
    except:
        pass
    time.sleep(random.randint(10, 15))
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeDailySetQuiz(browser: WebDriver, cardNumber: int,donepoints: int,DAILYTOTALPOINTS:int,DAILYPOINTSREPORTING:str):
    time.sleep(4)
    try:
        browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a').click()
        time.sleep(1)
        browser.switch_to.window(window_name=browser.window_handles[1])
        time.sleep(8)
        waitUntilpanelshow(browser)
        
    except Exception as e:
        try:
           browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
           time.sleep(1)
           browser.switch_to.window(window_name=browser.window_handles[1])
           time.sleep(8)
           waitUntilpanelshow(browser)
        except:   
            print(e)
    loaded = False
    thereBtn=False
    while(loaded == False):
        try:
            browser.find_element_by_xpath('//*[@id="rqStartQuiz"]')
            loaded = True
            thereBtn=True
        except:
            time.sleep(0.5)
            try:
                browser.find_element_by_xpath(
                    '//*[@id="currentQuestionContainer"]')
                loaded = True
            except Exception as e: # work on python 3.x
                print("daily quiz" + e)
                #resetTabs(browser)
    time.sleep(9)
    
    if thereBtn:
         browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
         time.sleep(3)
    try:
        waitUntilVisible(browser, By.XPATH,
                     '//*[@id="currentQuestionContainer"]/div/div[1]', 10)
        time.sleep(3)
        numberOfQuestions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.maxQuestions")
        numberOfOptions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.numberOfOptions")
        for question in range(numberOfQuestions):
            if numberOfOptions == 8:
                answers = []
                for i in range(8):  
                     try:
                        if browser.find_element_by_id("rqAnswerOption" + str(i)).get_attribute("isCorrectOption") == "True":
                           answers.append("rqAnswerOption" + str(i))
                     except:   
                       pass
                   
                for answer in answers:
                   try:
                         time.sleep(4)
                         browser.find_element_by_id(answer).click()
                         time.sleep(8)
                         tries = 0
                   except:
                        pass   

                while False:
                    try:
                        browser.find_elements_by_class_name('rqECredits')[0]
                        break
                    except IndexError:
                        if tries < 10:
                            tries += 1
                            time.sleep(0.5)
                        else:
                            browser.refresh()
                            tries = 0
                            time.sleep(5)
                time.sleep(5)
            elif numberOfOptions == 4:
                correctOption = browser.execute_script(
                 "return _w.rewardsQuizRenderInfo.correctAnswer")
                for i in range(4):
                    try:
                        time.sleep(4)
                        if browser.find_element_by_id("rqAnswerOption" + str(i)).get_attribute("data-option") == correctOption:
                            browser.find_element_by_id(
                            "rqAnswerOption" + str(i)).click()
                        time.sleep(8)
                        tries = 0
                        while False:
                          try:
                            browser.find_elements_by_class_name('rqECredits')[
                                0]
                            break
                          except IndexError:
                            if tries < 10:
                                tries += 1
                                time.sleep(0.5)
                            else:
                                browser.refresh()
                                tries = 0
                                time.sleep(5)
                        #break
                        #time.sleep(5)
                    except:
                        pass    
         
        DAILYTOTALPOINTS+=donepoints
        DAILYPOINTSREPORTING+=["done completeDailySetQuiz for "+str(donepoints)+"  \n"]       
        return DAILYTOTALPOINTS,DAILYPOINTSREPORTING 
    except Exception as e:
        print(e.message, e.args)
        print(str(e))
        #resetTabs()
    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)

def completeDailySetVariableActivity(browser: WebDriver, cardNumber: int,donepoints: int,DAILYTOTALPOINTS:int,DAILYPOINTSREPORTING:str ):
    time.sleep(2)
    try:
       browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a').click()
       time.sleep(1)
       browser.switch_to.window(window_name=browser.window_handles[1])
       time.sleep(8)
    except:
        try:
            browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
            time.sleep(1)
            browser.switch_to.window(window_name=browser.window_handles[1])
            time.sleep(8)
        except:
            pass    
    try:
        time.sleep(8)
        browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
        waitUntilVisible(browser, By.XPATH,
                         '//*[@id="currentQuestionContainer"]/div/div[1]', 3)
    except (NoSuchElementException, TimeoutException):
        try:
            counter = str(browser.find_element_by_xpath(
                '//*[@id="QuestionPane0"]/div[2]').get_attribute('innerHTML'))[:-1][1:]
            numberOfQuestions = max([int(s)
                                    for s in counter.split() if s.isdigit()])
            for question in range(numberOfQuestions):
                browser.execute_script('document.evaluate("//*[@id=\'QuestionPane' + str(question) + '\']/div[1]/div[2]/a[' + str(
                    random.randint(1, 3)) + ']/div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()')
                time.sleep(5)
                try:
                  browser.find_element_by_xpath(
                      '//*[@id="AnswerPane' + str(question) + '"]/div[1]/div[2]/div[4]/a/div/span/input').click()
                  time.sleep(7)
                except:
                    pass
                try:
                  browser.find_element_by_class_name("wk_button").click()
                except:
                    pass
           
            DAILYTOTALPOINTS+=donepoints
            DAILYPOINTSREPORTING+=["done completeDailySetVariableActivityfor "+str(donepoints)+"  \n"]
            time.sleep(5)
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])
            time.sleep(2)
            return DAILYTOTALPOINTS,DAILYPOINTSREPORTING
        except NoSuchElementException:
            time.sleep(random.randint(5, 9))
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])
            time.sleep(2)
            return
    time.sleep(3)
    correctAnswer = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.correctAnswer")
    if browser.find_element_by_id("rqAnswerOption0").get_attribute("data-option") == correctAnswer:
        browser.find_element_by_id("rqAnswerOption0").click()
    else:
        browser.find_element_by_id("rqAnswerOption1").click()
    time.sleep(10)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)

def waitUntilStartbuttonappear(browser: WebDriver):
    isbuttonLoaded=False
    timeFrame=1
    while(isbuttonLoaded == False):
        try:
            browser.find_element_by_xpath('//*[@id="rqStartQuiz"]')
            isbuttonLoaded = True
            return
        except:
            time.sleep(timeFrame*3)
            if(timeFrame==3):return
            timeFrame+=1

def completeDailySetThisOrThat(browser: WebDriver, cardNumber: int,totalpoints: int,DAILYTOTALPOINTS:int,DAILYPOINTSREPORTING:str):
    time.sleep(2)
    try:
       browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a').click()
    except:
        try:
          browser.find_element_by_xpath('//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
        except Exception as e:
            pass
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    waitUntilpanelshow(browser)
    thereBtn=False
    loaded=False
    time.sleep(7)
    waitUntilStartbuttonappear(browser)
    while(loaded == False):
        try:
            browser.find_element_by_xpath('//*[@id="rqStartQuiz"]')
            loaded = True
            thereBtn=True
        except:
            time.sleep(0.5)
            try:
                browser.find_element_by_xpath(
                    '//*[@id="currentQuestionContainer"]')
                loaded = True
            except Exception as e: # work on python 3.x
                print("daily quiz" + e)
                #resetTabs(browser)
    time.sleep(3)
    if thereBtn:
         browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
         time.sleep(3)
    try:
       waitUntilVisible(browser, By.XPATH,
                     '//*[@id="currentQuestionContainer"]/div/div[1]', 10)
       time.sleep(3)
       for question in range(10):
        try:
               time.sleep(8)
               answerEncodeKey = browser.execute_script("return _G.IG")
               answer1 = browser.find_element_by_id("rqAnswerOption0")
               answer1Title = answer1.get_attribute('data-option')
               answer1Code = getAnswerCode(answerEncodeKey, answer1Title)
               answer2 = browser.find_element_by_id("rqAnswerOption1")
               answer2Title = answer2.get_attribute('data-option')
               answer2Code = getAnswerCode(answerEncodeKey, answer2Title)
               correctAnswerCode = browser.execute_script(
                    "return _w.rewardsQuizRenderInfo.correctAnswer")

               if (answer1Code == correctAnswerCode):
                    answer1.click()
                    time.sleep(8)
               elif (answer2Code == correctAnswerCode):
                    answer2.click()
                    time.sleep(8)
        except Exception as e:
                pass    

       resetTabs(browser)
       DAILYTOTALPOINTS+=totalpoints
       DAILYPOINTSREPORTING+=["done completeDailySetThisOrThat for "+str(totalpoints)+"  \n"]     
       return DAILYTOTALPOINTS,DAILYPOINTSREPORTING
    except:
         resetTabs(browser)    

    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def getDashboardData(browser: WebDriver) -> dict:
    dashboard = findBetween(browser.find_element_by_xpath('/html/body').get_attribute('innerHTML'),
                            "var dashboard = ", ";\n        appDataModule.constant(\"prefetchedDashboard\", dashboard);")
    dashboard = json.loads(dashboard)
    return dashboard


def completeDailySet(browser: WebDriver,DAILYTOTALPOINTS:int,DAILYPOINTSREPORTING:str,PorgramTimeOut,ReportingP):
    if time.time() > PorgramTimeOut:reportTimeout("complete daily set",ReportingP), exit()
    resetTabs(browser)
    time.sleep(10)
    try:    
        if(browser.current_url.find("https://rewards.microsoft.com/welcome") != -1): 
             print("it must be loaded ")
             browser.execute_script(
            "document.getElementById('raf-signin-link-id').click()")
             time.sleep(7)
             print("ok")
    except Exception as e:
        print(e)

    d = getDashboardData(browser)['dailySetPromotions']
    todayDate = datetime.today().strftime('%m/%d/%Y')
    todayPack = []
    for date, data in d.items():
        if date == todayDate:
            todayPack = data
    for activity in todayPack:
        try:
            if activity['complete'] == False:
                cardNumber = int(activity['offerId'][-1:])
                if activity['promotionType'] == "urlreward":
                    print('[DAILY SET]',
                          'Completing search of card ' + str(cardNumber))
                    DAILYTOTALPOINTS,DAILYPOINTSREPORTING= completeDailySetSearch(browser, cardNumber,activity['pointProgressMax'],DAILYTOTALPOINTS,DAILYPOINTSREPORTING)
                if activity['promotionType'] == "quiz":
                    if activity['pointProgressMax'] == 50:
                        print(
                            '[DAILY SET]', 'Completing This or That of card ' + str(cardNumber))
                        DAILYTOTALPOINTS,DAILYPOINTSREPORTING=completeDailySetThisOrThat(browser, cardNumber,activity['pointProgressMax'],DAILYTOTALPOINTS,DAILYPOINTSREPORTING)
                    elif activity['pointProgressMax'] == 40 or activity['pointProgressMax'] == 30:
                        print('[DAILY SET]',
                              'Completing quiz of card ' + str(cardNumber))
                        DAILYTOTALPOINTS,DAILYPOINTSREPORTING=completeDailySetQuiz(browser, cardNumber,activity['pointProgressMax'],DAILYTOTALPOINTS,DAILYPOINTSREPORTING)
                    elif activity['pointProgressMax'] == 10:
                        searchUrl = urllib.parse.unquote(urllib.parse.parse_qs(
                            urllib.parse.urlparse(activity['destinationUrl']).query)['ru'][0])
                        searchUrlQueries = urllib.parse.parse_qs(
                            urllib.parse.urlparse(searchUrl).query)
                        filters = {}
                        for filter in searchUrlQueries['filters'][0].split(" "):
                            filter = filter.split(':', 1)
                            filters[filter[0]] = filter[1]
                        if "PollScenarioId" in filters:
                            print(
                                '[DAILY SET]', 'Completing poll of card ' + str(cardNumber))
                            DAILYTOTALPOINTS,DAILYPOINTSREPORTING=completeDailySetSurvey(browser, cardNumber,activity['pointProgressMax'],DAILYTOTALPOINTS,DAILYPOINTSREPORTING)
                        else:
                            print(
                                '[DAILY SET]', 'Completing quiz of card ' + str(cardNumber))
                            DAILYTOTALPOINTS,DAILYPOINTSREPORTING=completeDailySetVariableActivity(
                                browser, cardNumber,activity['pointProgressMax'],DAILYTOTALPOINTS,DAILYPOINTSREPORTING)
            
        except Exception as e:
            print(e)
            #resetTabs(browser) 
    return DAILYTOTALPOINTS,DAILYPOINTSREPORTING

def getAccountPoints(browser: WebDriver) -> int:
    return getDashboardData(browser)['userStatus']['availablePoints']


def completePunchCard(browser: WebDriver, url: str, childPromotions: dict):
    browser.get(url)
    for child in childPromotions:
        if child['complete'] == False:
            if child['promotionType'] == "urlreward":
                browser.execute_script(
                    "document.getElementsByClassName('offer-cta')[0].click()")
                time.sleep(1)
                browser.switch_to.window(window_name=browser.window_handles[1])
                time.sleep(random.randint(13, 17))
                browser.close()
                time.sleep(2)
                browser.switch_to.window(window_name=browser.window_handles[0])
                time.sleep(2)
            if child['promotionType'] == "quiz":
                browser.execute_script(
                    "document.getElementsByClassName('offer-cta')[0].click()")
                time.sleep(1)
                browser.switch_to.window(window_name=browser.window_handles[1])
                time.sleep(8)
                counter = str(browser.find_element_by_xpath(
                    '//*[@id="QuestionPane0"]/div[2]').get_attribute('innerHTML'))[:-1][1:]
                numberOfQuestions = max(
                    [int(s) for s in counter.split() if s.isdigit()])
                for question in range(numberOfQuestions):
                    browser.execute_script('document.evaluate("//*[@id=\'QuestionPane' + str(question) + '\']/div[1]/div[2]/a[' + str(
                    random.randint(1, 3)) + ']/div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()')
                time.sleep(5)
                try:
                  browser.find_element_by_xpath(
                      '//*[@id="AnswerPane' + str(question) + '"]/div[1]/div[2]/div[4]/a/div/span/input').click()
                  time.sleep(3)
                except:
                    pass
                browser.find_element_by_class_name("wk_button").click()
                time.sleep(3)
                time.sleep(5)
                browser.close()
                time.sleep(2)
                browser.switch_to.window(window_name=browser.window_handles[0])
                time.sleep(2)


def completePunchCards(browser: WebDriver):
    punchCards = getDashboardData(browser)['punchCards']
    for punchCard in punchCards:
        try:
            if punchCard['parentPromotion'] != None and punchCard['childPromotions'] != None and punchCard['parentPromotion']['complete'] == False and punchCard['parentPromotion']['pointProgressMax'] != 0:
                url = punchCard['parentPromotion']['attributes']['destination']
                path = url.replace(
                    'https://rewards.microsoft.com/dashboard/', '')
                userCode = path[:4]
                dest = 'https://rewards.microsoft.com/dashboard/' + \
                    userCode + path.split(userCode)[1]
                completePunchCard(browser, dest, punchCard['childPromotions'])
        except Exception as e:
            resetTabs(browser)
    time.sleep(2)
    browser.get('https://account.microsoft.com/rewards/')
    time.sleep(2)


def completeMorePromotionSearch(browser: WebDriver, cardNumber: int,donepoints: int,PROMOTIONPOINTS:int,PROMOTIONREPOTING:str  ):
    try:
        browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a').click()
    except:
        try:
           browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/a').click()
        except: 
           pass   

    
    PROMOTIONPOINTS+=donepoints
    PROMOTIONREPOTING+=["done completeMorePromotionSearch for "+str(donepoints)+"  \n"]    
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(random.randint(13, 17))
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)
    return PROMOTIONREPOTING,PROMOTIONPOINTS


def completeMorePromotionQuiz(browser: WebDriver, cardNumber: int,donepoints: int,PROMOTIONPOINTS:int,PROMOTIONREPOTING:str):
    try:
       browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a').click()
    except:
      try:
         browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/a').click()
      except: 
           pass   

    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    waitUntilpanelshow(browser)
    loaded = False
    thereBtn=False
    while(loaded == False):
        try:
            browser.find_element_by_xpath('//*[@id="rqStartQuiz"]')
            loaded = True
            thereBtn=True
        except:
            time.sleep(0.5)
            try:
                browser.find_element_by_xpath(
                    '//*[@id="currentQuestionContainer"]')
                loaded = True
            except Exception as e: # work on python 3.x
                print("daily quiz" + e)
                #resetTabs(browser)
    time.sleep(3)
    if thereBtn:
         browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
         time.sleep(3)
    try:
        waitUntilVisible(browser, By.XPATH,
                     '//*[@id="currentQuestionContainer"]/div/div[1]', 10)
        time.sleep(3)
        numberOfQuestions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.maxQuestions")
        numberOfOptions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.numberOfOptions")
        for question in range(numberOfQuestions):
            if numberOfOptions == 8:
                answers = []
                for i in range(8):
                    try:
                        if browser.find_element_by_id("rqAnswerOption" + str(i)).get_attribute("isCorrectOption") == "True":
                           answers.append("rqAnswerOption" + str(i))
                    except:   
                       pass
                for answer in answers:
                    try:
                      browser.find_element_by_id(answer).click()
                    except:
                        pass
                    time.sleep(5)
                    tries = 0
                while False:
                    try:
                        browser.find_elements_by_class_name('rqECredits')[0]
                        break
                    except IndexError:
                        if tries < 10:
                            tries += 1
                            time.sleep(0.5)
                        else:
                            browser.refresh()
                            tries = 0
                            time.sleep(5)
                time.sleep(5)
            elif numberOfOptions == 4:
                correctOption = browser.execute_script(
                 "return _w.rewardsQuizRenderInfo.correctAnswer")
                for i in range(4):
                    try:
                        if browser.find_element_by_id("rqAnswerOption" + str(i)).get_attribute("data-option") == correctOption:
                            try:
                                browser.find_element_by_id(
                            "rqAnswerOption" + str(i)).click()
                            except:
                                pass
                        time.sleep(5)
                        tries = 0
                        while False:
                          try:
                            browser.find_elements_by_class_name('rqECredits')[
                                0]
                            break
                          except IndexError:
                            if tries < 10:
                                tries += 1
                                time.sleep(0.5)
                            else:
                                browser.refresh()
                                tries = 0
                                time.sleep(5)
                        #break
                        #time.sleep(5)
                    except:
                        pass    
        
        PROMOTIONPOINTS+=donepoints
        PROMOTIONREPOTING+=["done completeMorePromotionQuiz for "+str(donepoints)+"  \n"]
        
    except:
        resetTabs()
    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)
    return PROMOTIONREPOTING,PROMOTIONPOINTS


def completeMorePromotionABC(browser: WebDriver, cardNumber: int,donepoints: int,PROMOTIONPOINTS:int,PROMOTIONREPOTING:str  ):
  try:
    try:
          browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a').click()
    except:
        try:
             browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/a').click()
        except: 
           pass  
         
    
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    counter = str(browser.find_element_by_xpath(
        '//*[@id="QuestionPane0"]/div[2]').get_attribute('innerHTML'))[:-1][1:]
    numberOfQuestions = max([int(s) for s in counter.split() if s.isdigit()])
    for question in range(numberOfQuestions):
                browser.execute_script('document.evaluate("//*[@id=\'QuestionPane' + str(question) + '\']/div[1]/div[2]/a[' + str(
                    random.randint(1, 3)) + ']/div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()')
                time.sleep(5)
                try:
                  browser.find_element_by_xpath(
                      '//*[@id="AnswerPane' + str(question) + '"]/div[1]/div[2]/div[4]/a/div/span/input').click()
                  time.sleep(3)
                except:
                    pass
                browser.find_element_by_class_name("wk_button").click()
                time.sleep(3)
    time.sleep(5)
    PROMOTIONPOINTS+=donepoints
    PROMOTIONREPOTING+=["done completeMorePromotionABC for "+str(donepoints)+"  \n"]
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)
    return PROMOTIONREPOTING,PROMOTIONPOINTS
  except:
      pass


 


def completeMorePromotionThisOrThat(browser: WebDriver, cardNumber: int,donepoints: int,PROMOTIONPOINTS:int,PROMOTIONREPOTING:str):
    try:
        browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a').click()
    except:
        try:
           browser.find_element_by_xpath('//*[@id="more-activities"]/div/mee-card[' + str(
        cardNumber) + ']/div/card-content/mee-rewards-more-activities-card-item/div/a').click()
        except: 
           pass    
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    waitUntilpanelshow(browser)
    loaded = False
    thereBtn=False
    while(loaded == False):
        try:
            browser.find_element_by_xpath('//*[@id="rqStartQuiz"]')
            loaded = True
            thereBtn=True
        except:
            time.sleep(0.5)
            try:
                browser.find_element_by_xpath(
                    '//*[@id="currentQuestionContainer"]')
                loaded = True
            except Exception as e: # work on python 3.x
                print("daily quiz" + e)
                #resetTabs(browser)
    time.sleep(3)
    if thereBtn:
         browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
         time.sleep(3)
    try:
       waitUntilVisible(browser, By.XPATH,
                     '//*[@id="currentQuestionContainer"]/div/div[1]', 10)
       time.sleep(3)
       for question in range(10):
        try:    
               time.sleep(8)
               answerEncodeKey = browser.execute_script("return _G.IG")
               answer1 = browser.find_element_by_id("rqAnswerOption0")
               answer1Title = answer1.get_attribute('data-option')
               answer1Code = getAnswerCode(answerEncodeKey, answer1Title)
               answer2 = browser.find_element_by_id("rqAnswerOption1")
               answer2Title = answer2.get_attribute('data-option')
               answer2Code = getAnswerCode(answerEncodeKey, answer2Title)
               correctAnswerCode = browser.execute_script(
                    "return _w.rewardsQuizRenderInfo.correctAnswer")

               if (answer1Code == correctAnswerCode):
                    answer1.click()
                    time.sleep(8)
               elif (answer2Code == correctAnswerCode):
                    answer2.click()
                    time.sleep(8)
        except:
                pass        
       
       PROMOTIONPOINTS+=donepoints
       PROMOTIONREPOTING+=["done completeMorePromotionThisOrThat for "+str(donepoints)+"  \n"]
       
    except:
         resetTabs(browser)    

    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)
    return PROMOTIONREPOTING,PROMOTIONPOINTS

def checkifmorepromotionexist(browser: WebDriver):
   
    try:
        resetTabs(browser)
        morePromotions = getDashboardData(browser)['morePromotions']
        isfinish=True
        i = 0
        for promotion in morePromotions:
            try:
                i += 1
                if promotion['complete'] == False and promotion['pointProgressMax'] != 0:
                    
                    if promotion['promotionType'] == "urlreward":
                        isfinish=False
                    elif promotion['promotionType'] == "quiz":
                        if promotion['pointProgressMax'] == 10:
                            isfinish=False
                        elif promotion['pointProgressMax'] == 30 or promotion['pointProgressMax'] == 40:
                            isfinish=False
                        elif promotion['pointProgressMax'] == 50:
                             isfinish=False
                    else:
                        if promotion['pointProgressMax'] == 100 or promotion['pointProgressMax'] == 200:
                            isfinish=False
            except Exception as e:
                print(e)
                pass    
        return isfinish
    except Exception as e:
        print(e)
        checkifmorepromotionexist(browser)
def checkifdailypromotionexist(browser: WebDriver):
    resetTabs(browser)
    d = getDashboardData(browser)['dailySetPromotions']
    todayDate = datetime.today().strftime('%m/%d/%Y')
    todayPack = []
    isfinish=True
    for date, data in d.items():
        if date == todayDate:
            todayPack = data
    for activity in todayPack:
        try:
            if activity['complete'] == False:
                cardNumber = int(activity['offerId'][-1:])
                if activity['promotionType'] == "urlreward":
                    isfinish=False
                if activity['promotionType'] == "quiz":
                    if activity['pointProgressMax'] == 50:
                      isfinish=False
                    elif activity['pointProgressMax'] == 40 or activity['pointProgressMax'] == 30:
                       isfinish=False
                    elif activity['pointProgressMax'] == 10:
                        searchUrl = urllib.parse.unquote(urllib.parse.parse_qs(
                            urllib.parse.urlparse(activity['destinationUrl']).query)['ru'][0])
                        searchUrlQueries = urllib.parse.parse_qs(
                            urllib.parse.urlparse(searchUrl).query)
                        filters = {}
                        for filter in searchUrlQueries['filters'][0].split(" "):
                            filter = filter.split(':', 1)
                            filters[filter[0]] = filter[1]
                        if "PollScenarioId" in filters:
                           isfinish=False
                        else:
                           isfinish=False
        except:
            resetTabs(browser)
    return isfinish

def completeMorePromotions(browser: WebDriver,PROMOTIONPOINTS:int,PROMOTIONREPOTING:str,PorgramTimeOut,ReportingP ):
   try:
        if time.time() > PorgramTimeOut:reportTimeout("complete more promotion",ReportingP), exit()
        resetTabs(browser)
        morePromotions = getDashboardData(browser)['morePromotions']
        i = 0
        for promotion in morePromotions:
            try:
                i += 1
                if promotion['complete'] == False and promotion['pointProgressMax'] != 0:
                    if promotion['promotionType'] == "urlreward":
                        PROMOTIONREPOTING,PROMOTIONPOINTS=completeMorePromotionSearch(browser, i,promotion['pointProgressMax'],PROMOTIONPOINTS,PROMOTIONREPOTING)
                    elif promotion['promotionType'] == "quiz":
                        if promotion['pointProgressMax'] == 10:
                             PROMOTIONREPOTING,PROMOTIONPOINTS= completeMorePromotionABC(browser, i,promotion['pointProgressMax'],PROMOTIONPOINTS,PROMOTIONREPOTING)
                        elif promotion['pointProgressMax'] == 30 or promotion['pointProgressMax'] == 40:
                            PROMOTIONREPOTING,PROMOTIONPOINTS=completeMorePromotionQuiz(browser, i,promotion['pointProgressMax'],PROMOTIONPOINTS,PROMOTIONREPOTING)
                        elif promotion['pointProgressMax'] == 50:
                             PROMOTIONREPOTING,PROMOTIONPOINTS= completeMorePromotionThisOrThat(browser, i,promotion['pointProgressMax'],PROMOTIONPOINTS,PROMOTIONREPOTING)
                    else:
                        if promotion['pointProgressMax'] == 100 or promotion['pointProgressMax'] == 200:
                            PROMOTIONREPOTING,PROMOTIONPOINTS=completeMorePromotionSearch(browser, i,promotion['pointProgressMax'],PROMOTIONPOINTS,PROMOTIONREPOTING)
            except Exception as e:
                print(e)
                resetTabs(browser)
                completeMorePromotions(browser,PROMOTIONPOINTS,PROMOTIONREPOTING,PorgramTimeOut,ReportingP)
                #resetTabs(browser)
        return PROMOTIONREPOTING,PROMOTIONPOINTS
   except Exception as e:
        print(e)
        if time.time() > PorgramTimeOut:reportTimeout("complete more promotion",ReportingP), exit()
        resetTabs(browser)
        completeMorePromotions(browser,PROMOTIONPOINTS,PROMOTIONREPOTING,PorgramTimeOut,ReportingP)

def getRemainingSearches(browser: WebDriver):
    dashboard = getDashboardData(browser)
    searchPoints = 1
    counters = dashboard['userStatus']['counters']
    progressDesktop = counters['pcSearch'][0]['pointProgress'] + \
        counters['pcSearch'][1]['pointProgress']
    targetDesktop = counters['pcSearch'][0]['pointProgressMax'] + \
        counters['pcSearch'][1]['pointProgressMax']
    if targetDesktop == 33:
        # Level 1 EU
        searchPoints = 3
    elif targetDesktop == 55:
        # Level 1 US
        searchPoints = 5
    elif targetDesktop == 102:
        # Level 2 EU
        searchPoints = 3
    elif targetDesktop >= 170:
        # Level 2 US
        searchPoints = 5
    remainingDesktop = int((targetDesktop - progressDesktop) / searchPoints)
    remainingMobile = 0
    if dashboard['userStatus']['levelInfo']['activeLevel'] != "Level1":
        progressMobile = counters['mobileSearch'][0]['pointProgress']
        targetMobile = counters['mobileSearch'][0]['pointProgressMax']
        remainingMobile = int((targetMobile - progressMobile) / searchPoints)
    return(remainingDesktop, remainingMobile)


def Get_point_total(browser: WebDriver, POINTS_COUNTER: str,logfileDir:str,AccountemailAddress:str):

    try:

        # Append-adds at last
        file1 = open(logfileDir, "a")  # append mode
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        file1.write("Today is "+dt_string+" email is : " +
                    AccountemailAddress+" and balance : " + str(POINTS_COUNTER)+"  \n")
        file1.close()
    except Exception as e:
        print(e)
