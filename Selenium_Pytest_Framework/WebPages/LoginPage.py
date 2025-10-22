from TestCases.configuration import *
from Utils.Actions import Actions
from selenium.webdriver.common.by import By

class Login_Page(Actions):

    username_ele = (By.XPATH,'//input[@name="username"]')
    pwd_ele = (By.XPATH,'//input[@name="password"]')
    login_buttton_ele = (By.XPATH,'//button')

    # Pay attention to the syntax of inheritance!!!!
    # Never forget to pass self and parameters(e.g. driver) to both __init__()!!!
    def __init__(self, driver):
        Actions.__init__(self, driver)

    def login(self, username, password):
        self.element_sendkeys_until(locator=self.username_ele,text=username)
        self.element_sendkeys_until(locator=self.pwd_ele, text=password)
        self.element_click_until(locator=self.login_buttton_ele)

