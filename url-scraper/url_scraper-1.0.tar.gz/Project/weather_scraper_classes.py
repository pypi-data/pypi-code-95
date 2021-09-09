import sys
sys.path.append('..')
from main_classes import *
from common_functions import *

class Weather_Xpath_Selection():
    """
    This is where the user can change certain xpaths easily without having to find all the usages in the code. 

    These cover the xpaths on the weather website. The function title normally contains the name of the usual variable name making it easy to type in and refer to. 
    These all return strings 

    TD: Make this a subclass of some sort of all encompassing variable selector. 

    """
    def get_search_button():
        return '/html/body/app-root/app-history-search/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div/div/div/div/form/lib-date-selector/div/input'
    def get_high_temp():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[1]/tr[1]/td[1]'
    def get_low_temp():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[1]/tr[2]/td[1]'
    def get_temp_average():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[1]/tr[3]/td[1]'
    def get_precipitation_number():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[2]/tr/td[1]'
    def get_dew_point():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[3]/tr[1]/td[1]'
    def get_dew_high():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[3]/tr[2]/td[1]'
    def get_dew_low():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[3]/tr[3]/td[1]'
    def get_dew_average():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[3]/tr[4]/td[1]'
    def get_max_wind_speed():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[4]/tr[1]/td[1]'
    def get_visibility():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[4]/tr[2]/td[1]'
    def get_day_length():
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[6]/tr[1]/td[1]'

    def get_observations_body():
        """
        This Xpath refers to the table where the timely specific variables occur agaisnt their time of day. 
        """
        return '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[5]/div[1]/div/lib-city-history-observation/div/div[2]/table/tbody'

#TD This ideally should not be needed here but code wouldn't work without it. Find out how to improve this.  
weather_xpaths = Weather_Xpath_Selection
test_month_location_match = [{'Month': ('2020', 'November'), 'Locations' : ['New York' ,'London', 'Tokyo']},{'Month': ('2020', 'September'), 'Locations' : ['Tokyo' ,'London', 'Hong Kong']}, {'Month': ('2021', 'March'), 'Locations' : ['New York' ,'London', 'Oslo']}]
test_location_key_match = [{'Location Name': 'New York','key': 'KLGA'}, {'Location Name': 'London','key': 'EGLC'}, {'Location Name': 'Tokyo' ,'key': 'RJTT'}, {'Location Name': 'Hong Kong','key': 'VHHH'}, {'Location Name': 'Oslo','key': 'ENGM'}, ]

class Weather_Scrape(Scraping_Space):
    """
    This is the class that does the web scraping for the weather it has many layers.
    """
    def __init__(self, Giant_dataset, location_key_match, month_location_match):
        """
        saved_webscraper is where the data gets stored and saved. 
        """
        super().__init__()
        self.Giant_dataset = Giant_dataset
        self.Giant_dataset = []
        self.location_key_match = location_key_match
        self.saved_weather_scraper = []
        self.month_location_match = month_location_match

    def reset_dataset(self):
        """
        This resets the huge list which is being scraped through. 
        """
        self.Giant_dataset = []
    


    def complete_weather_scrape(self):
        """
        This funciton gets all the data for each month, month by month. It puts all the data into the Giant_datasert
        """
        for months in self.month_location_match:
            self.month_year_weather_scrape(months)


    def month_year_weather_scrape(self, months):
        """
        This scrapes the data for all location for this month 
        """
        current_month_list = []
        current_month_dict = {}
        current_year, current_month = seperate_month_and_year(months['Month'])
        month_info = Month_And_Year(month = current_month, year = current_year)
        month_number = month_info.get_month_number()
        


        current_month_dict['Month'] = (current_month, current_year) #These last two enteries correspond to the month of the year and the year. 
        current_month_dict['Data'] = [] 
        

        for locations in months['Locations']:  #We are finding the key for each location here.
            self.location_and_month_scrape(locations, month_info.get_amount_of_days(), current_year, month_number, current_month_dict, current_month_list)
            save_data(f"{current_month} + {current_year} + info", current_month_dict) # Data is being saved here.
            
            
        self.Giant_dataset.append(current_month_dict)  #Add the month's data to the giant dataset. 



    def location_and_month_scrape(self, locations, amount_of_days, current_year, month_number, current_month_dict, current_month_list):
        """
        This scrapes all the data for this combination of location and month 
        """
        current_key = 'a'

        #Good use for a search function here. 
        for enteries in self.location_key_match:
            if enteries['Location Name'] == locations:
                current_key = enteries['key']    #The key is found.

    
        for i in range(1, amount_of_days + 1):  #This range means for every day of the month
            current_month_list.append(self.day_scrape(i, locations, current_key, current_year, month_number, current_month_dict))
            
        return(current_month_list)
        





    
    def try_daily_observations_scraping(self, current_date_dict, driver):  # This is a fucntion which scrapes from the table in the weather section.
        """
        The attempt to try to scrape the specific daily info
        """
        time_data = []
        try:
            self.daily_observation_scraping_attempt(current_date_dict, driver)

       
        except:
            current_date_dict['Time_Data'] = time_data


    def daily_observation_scraping_attempt(self, current_date_dict, driver):
        """
        The scraping of the specific daily info assuming it is possible. 
        """

        list_of_rows = self.get_all_children(driver, weather_xpaths.get_observations_body())
        time_data = []
        for row in list_of_rows:
            self.get_time_of_day_weather_information(row, time_data)


        current_date_dict['Time_Data'] = time_data
        return(current_date_dict)
    
    def get_time_of_day_weather_information(self, row, time_data):
        """
        This method gets the information for specific times of days throughout the day. 
        """
        time_condition = {} # A dictionary recording data for each time in the day in the table. 
        column_number = 1 # Start with the leftmost column. 

        row_elements = row.find_elements_by_xpath("*")

        for column in row_elements:
            time_data.append(self.time_of_day_column_scrape(column, column_number, time_condition))
            column_number += 1



        time_data.append(time_condition) 
        return time_data      #collect all the time data together and add them to the dictionary. 
        
    @staticmethod
    def time_of_day_column_scrape(column, column_number, time_condition):
        """
        This method goes through a specific row of the table. 
        """
        print(column_number)
        if column_number == 1:
            time_condition['Time'] = column.text # This column is the time column. 
        if column_number == 5: 
            time_condition['Wind_Direction'] = column.text #This column is the wind direction column. 
        if column_number == 10:
            time_condition['Rain_Condition'] = column.text   #This column is the worded rain column. 
        return(time_condition)
        

    def day_scrape(self, i, locations, current_key, current_year, month_number, current_month_dict):
        """
        This scrapes all the information for a single day and location. 
        """
        time.sleep(our_parameters.return_weather_sleeping_list()[0]) 

        driver = webdriver.Chrome('chromedriver.exe')
        current_date_dict = {}
        current_date_dict['day_and_location'] = {'day': i,'location': locations}  #Input the independent variables into the dictionary

        desired_url =  f"https://www.wunderground.com/history/daily/{current_key}/date/{current_year}-{month_number}-{i}"
        driver.get(desired_url)

        time.sleep(our_parameters.return_weather_sleeping_list()[1])

        self.trying_scraping(current_date_dict, driver)   #We are using the two previous functions for scraping these pages
        self.try_daily_observations_scraping(current_date_dict, driver)
        print(current_date_dict)
        driver.close
        current_month_dict['Data'].append(current_date_dict)   #Add all this date to the data value of this month   

    @staticmethod
    def trying_scraping(current_date_dict, driver):  # This function tries scraping from the locations on the weather website. These are try statements so if a page has no info, no info is added.
        """
        For different Xpaths, this method goes one by one in trying to get the data from them. 
        """
        try:
       
            high_temp = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[1]/tr[1]/td[1]')
            current_date_dict['High_Temp'] = high_temp.text
        except:
            pass
        
        try:
            low_temp = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[1]/tr[2]/td[1]')
            current_date_dict['Low_Temp'] = low_temp.text
        except:
            pass

        try:
            day_average = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[1]/tr[3]/td[1]')
            current_date_dict['Day_Average_Temp'] = day_average.text
        except:
            pass

        try:
            precipitation_number = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[2]/tr/td[1]')
            current_date_dict['Precipitation_Number'] = precipitation_number.text
        except:
            pass

        try:
            dew_point = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[3]/tr[1]/td[1]')
            current_date_dict['Dew_point'] = dew_point.text
        except:
            pass

        try:
            dew_high = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[3]/tr[2]/td[1]')
            current_date_dict['Dew_High'] = dew_high.text
        except:
            pass

        try:
            dew_low = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[3]/tr[3]/td[1]')
            current_date_dict['Dew_Low'] = dew_low.text
        except:
            pass
        
        try:
            dew_average = driver.find_element_by_xpath('')
            current_date_dict['Dew_Average'] = dew_average.text
        except:
            pass
        
        try:
            max_wind_speed = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[4]/tr[1]/td[1]')
            current_date_dict['Max_Wind_Speed'] = max_wind_speed.text
        except:
            pass

        try:
            visibility = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[4]/tr[2]/td[1]')
            current_date_dict['Visibility'] = visibility.text
        except:
            pass

        try:
            day_length = driver.find_element_by_xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[2]/div[1]/div[3]/div[1]/div/lib-city-history-summary/div/div[2]/table/tbody[6]/tr[1]/td[1]')
            current_date_dict['Day_length'] = day_length.text
        except:
            pass
