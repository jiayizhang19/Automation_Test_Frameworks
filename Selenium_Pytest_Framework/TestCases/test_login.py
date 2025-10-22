
import pytest
import allure
from TestCases.configuration import * # this line could be deleted if name "configuration.py" as "conftest.py"
from WebPages.LoginPage import Login_Page


'''
Allure setup
1. Download Allure here: https://github.com/allure-framework/allure2
2. Add allure bin path to system variables Path
3. Ensure jdk's path in java_home is correctedly setup, as allure will need jdk
4. pip install allure-pytest
5. run command: pytest --alluredir=allure-results
6. View report command: allure serve allure-results
'''

@pytest.mark.usefixtures("browser_setup") # This line could be removed as soon as set autouse=True in browser_setup fixture

class Test_Login:

    # setup_class and teardown_class should be used if no yield defined in configuration browser_setup
    # def setup_class(self):
    #     self.driver.get(base_url)
    #     self.login_page = Login_Page(self.driver)

    @allure.description("Validate valid login credentials.")
    @allure.severity(severity_level="Critical")
    @pytest.mark.parametrize("username, password, expected_result", [
        ("valid_user", "valid_password", True),  # Valid credentials
        ("invalid_user", "valid_password", False),  # Invalid username
        ("valid_user", "invalid_password", False),  # Invalid password
        ("", "", False),  # Empty credentials
    ])
    def test_validate_login(self, username, password, expected_result):
        self.driver.get(base_url)
        Login_Page(self.driver).login(username, password)
        if expected_result:
            assert "dashboard" in self.driver.current_url, "Valid login failed!"
            allure.attach(
                self.driver.get_screenshot_as_png(), 
                name="Valid credentials", 
                attachment_type=allure.attachment_type.PNG
            )
        else:
            try:
                assert "dashboard" not in self.driver.current_url, "Invalid login passed unexpectedly!"
            finally:
                allure.attach(
                    self.driver.get_screenshot_as_png(), 
                    name="Invalid credentials", 
                    attachment_type=allure.attachment_type.PNG
                )

    # def teardown_class(self):
    #     self.driver.quit()

@pytest.mark.usefixtures("browser_setup") # This line could be removed as soon as set autouse=True in browser_setup fixture
class Test_Invalid_Login:

    @allure.description("Validate invalid login credentials.")
    @allure.severity(severity_level="Normal")
    def test_invalid_login(self):
        self.driver.get(base_url)
        Login_Page(self.driver).login(username, invalid_psw)
        try:
            assert "dashboard" in self.driver.current_url
        finally:
            if(AssertionError):
                allure.attach(self.driver.get_screenshot_as_png(), name="Invalid credentials",
                              attachment_type=allure.attachment_type.PNG)
