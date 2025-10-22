from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class Actions:

    def __init__(self,driver):
        self.driver = driver

    def element_sendkeys_until(self, locator, text):
        WebDriverWait(self.driver,10).until(
            expected_conditions.visibility_of_element_located(locator)
        ).send_keys(text)

    def element_click_until(self,locator):
        WebDriverWait(self.driver,10).until(
            expected_conditions.visibility_of_element_located(locator)
        ).click()