from selenium import webdriver
from os.path import isdir
from os import mkdir


#final_string = string + " IMAGES"
class Webscraper:
    def __init__(self) -> None:
       
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument("--remote-debugging-port=45447")
        self.driver = webdriver.Chrome(options=options)


    def search_string(self, data):
        
        """
        CREATES DIRECTORY WITH THE NAME OF SEARCH STRING
        OPENS URL ON GOOGLE CHROME WITH SEARCH STRING

        PARAMETERS:
        ==========
        data : str  search keyword
        
        """

        self.data = data
        if not isdir("tmp"):
            mkdir("tmp")

        if not isdir(f"tmp/{self.data}"):
            mkdir("tmp/"+self.data)

        self.driver.get(f'https://www.google.com/search?channel=fs&source=univ&tbm=isch&q={data}')


    def get_images_button(self):
        
        """
        GETS THE XPATH OF THE FIRST IMAGE FROM THE GOOGLE IMAGES
        """

        img_button = '//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]'
        return img_button
        

    def click_img_button(self):

        '''
        CLICK ON THE FIRST IMAGE FROM THE GOOGLE IMAGES
        '''

        img_click = self.get_images_button()
        self.driver.find_element_by_xpath(xpath=img_click).click()


    def after_click_image_loc(self):
        
        '''
        GETS THE XPATH AFTER CLICKING THE IMAGE
        '''

        img_location = '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[2]/div[1]/a/img'
        return img_location


    def screenshot_image(self,img_num):

        '''
        TAKES THE SCREENSHOT OF THE IMAGES
        '''

        img_ss = self.after_click_image_loc()
        self.driver.find_element_by_xpath(xpath=img_ss).screenshot(f'tmp/{self.data}/{self.data + img_num}.png')
        return f'tmp/{self.data}/{self.data + img_num}.png'

    def get_next_button(self):
        
        '''
        GETS THE XPATH OF THE NEXT BUTTON ON GOOGLE IMAGE
        '''
        
        next_button = '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[1]/a[3]'
        return next_button


    def click_next_button(self):
        
        '''
        AFTER TAKING SCREENSHOT CLICKS THE NEXT BUTTON ON GOOGLE IMAGE
        '''
        
        next_button_loc = self.get_next_button()
        self.driver.find_element_by_xpath(xpath=next_button_loc).click()


    def close(self):
        
        '''
        CLOSES THE CHROME
        '''

        self.driver.close()
