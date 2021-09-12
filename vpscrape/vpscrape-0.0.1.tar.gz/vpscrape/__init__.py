# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 21:06:39 2021
updated on 
@author: Vinson Phoan
Kominfo Scrape
https://www.kominfo.go.id/content/all/laporan_isu_hoaks

"""
#Import Library
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException       

class Scrape:
    def __init__(self, url, time, delay, debug):
       self.url = url
       self.redirect = None
       self.driver = None
       self.time = time
       self.delay = delay
       self.debug = debug
        
    def get_chrome_driver(self):
        try:
            self.driver = webdriver.Chrome('C:\chromedriver.exe')
        except Exception as e:
            print(e)
            
    def stop(self):
        if self.debug == False:
            self.driver.close()
        
    def connect(self):
        self.driver.get(self.url)
    
    def execute(self):
        self.get_chrome_driver()
        self.connect()
        
     
    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
    def check_exists_by_class(self, xpath):
       try:
           self.driver.find_elements_by_class_name(xpath)
       except NoSuchElementException:
           return False
       return True
        
    def get_information(self, commands):
        """
        Fungsi ini untuk mengeksekusi command dari codingan yang terdapat dari commands
       
        Parameters
        ----------
        commands : Array/List
            Berisi command dari selenium.
             Contoh: ["find_elements_by_class_name('title')", "find_elements_by_class_name('date')"]

        Returns
        -------
        data : Array/List
            Berisi informasi yang di scrap melalui command yang diberikan.

        """
        data = {}
        index = 0
        for idx, elem in commands.items():
            if elem['key'].lower().strip() == 'class':
                data[elem['value']] = {elem['value']:self.driver.find_elements_by_class_name(elem['value'])}
        #print(self.driver)
        #print("self.driver."+commands[0])
        #data = [exec(str(self.driver)+'.'+str(i)) for i in commands]
        #data = [self.driver.execute_script(i) for i in commands]
        return data