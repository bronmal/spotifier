from multiprocessing import Pool 
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from os import PathLike
from time import sleep
from parser import parse_accounts
from utils import Account, Browser
from os.path import isfile
from typing import Union




class mt_test(object):
    def __init__(self,url:str = 'http://www.spotifier.ru',accounts_path:PathLike = "mt_tester\\accounts.txt",proccesses=1,accounts_vk:list = None,accounts_sp:list = None,browser:Browser = Browser.Chrome):
        self.proccesses = proccesses
        self.url = url
        self.WebDriverPath = ""
        self.browser = browser
        self.accounts_vk,self.accounts_sp = parse_accounts(accounts_path)

    def get_driver(self):
        if self.browser == Browser.Firefox:
            self.WebDriverPath = "mt_tester\WebDriver\geckodriver.exe"
            if not isfile(self.WebDriverPath):
                raise Exception("Cant find Firefox WebDriver, you can download it here https://github.com/mozilla/geckodriver/releases")
            driver = webdriver.Firefox(executable_path = self.WebDriverPath)
        elif self.browser == Browser.Chrome:
            self.WebDriverPath = "mt_tester\WebDriver\chromedriver.exe"
            if not isfile(self.WebDriverPath):
                raise Exception("Cant find Chromium WebDriver, you can download it here https://chromedriver.chromium.org/downloads")
            driver = webdriver.Chrome(executable_path = self.WebDriverPath)
        elif self.browser == Browser.Edge:
            self.WebDriverPath = "mt_tester\WebDriver\msedgedriver.exe"
            if not isfile(self.WebDriverPath):
                raise Exception("Cant find Edge WebDriver, you can download it here https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            driver = webdriver.Edge(executable_path = self.WebDriverPath) 
        if driver:
            return driver


    def run_driver(self, i):
        driver = self.get_driver()
        driver.get(self.url)
        element = driver.find_element_by_id('btn')
        ActionChains(driver=driver).click(on_element=element).perform()

        self.wait_for_element_precense_by_xPath('/html/body/div/div/div[1]/div[3]/div/form/div[1]/input', driver)

        element = driver.find_element_by_xpath('/html/body/div/div/div[1]/div[3]/div/form/div[1]/input').send_keys(self.accounts_vk[i].login)
        
        element = driver.find_element_by_xpath('/html/body/div/div/div[1]/div[3]/div/form/div[2]/input').send_keys(self.accounts_vk[i].password)
        driver.find_element_by_xpath('/html/body/div/div/div[1]/div[3]/div/form/div[3]/p/input').click()

        self.wait_for_element_precense_by_xPath('//*[@id="auth_spotify"]', driver)


        driver.find_element_by_xpath('//*[@id="auth_spotify"]').click()

        self.wait_for_element_precense_by_xPath('//*[@id="login-username"]', driver)

        
        driver.find_element_by_xpath('//*[@id="login-username"]').send_keys(self.accounts_sp[i].login)
        driver.find_element_by_xpath('//*[@id="login-password"]').send_keys(self.accounts_sp[i].password)
        driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/form/div[4]/div[1]/div/label').click()
        driver.find_element_by_xpath('//*[@id="login-button"]').click()

        self.wait_for_element_precense_by_xPath('//*[@id="auth-accept"]', driver)

        driver.find_element_by_xpath('//*[@id="auth-accept"]').click()
        
        driver.close()

    def run(self):
        with Pool(processes=self.proccesses) as pool:
            pool.map(self.run_driver, range(self.proccesses))



    def wait_for_element_precense_by_xPath(self,xPath:str, driver):
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xPath)))
        except TimeoutException:
            print("Loading took too much time!")
            driver.close()
            return
        

if __name__ == '__main__':
    proccesses = 4
    mt_test(
     proccesses=procceses,
     browser=Browser.Firefox
    ).run()
