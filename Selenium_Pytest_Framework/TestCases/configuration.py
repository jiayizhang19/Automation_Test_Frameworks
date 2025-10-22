import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


base_url = 'https://opensource-demo.orangehrmlive.com/web/index.php/auth/login'
username = "Admin"
password = "admin123"
invalid_psw = "21"


'''
If name this file as conftest.py, then pytest will automatically pick this up before execution, and so no need to import this file in test_.py

Fixture scope:
1. function: run once for each test function
    --> use @pytest.fixture(autouse=True) to run the fixture automatically without calling it in the test function
    --> if not setting autouse=True in configuration file, then need to pass the name of this fixture as an argumment into the test case to call it like the below
        def test_case_1(name_of_fixture):
            ...
2. class: run once for each class of tests
    --> use @pytest.fixture(scope="class",autouse=True) to run the fixture automatically without calling it in the test class
    --> if not setting autouse=True in configuration file, then need to pass the name of this fixture before the test case class to call it like the below
    @pytest.mark.usefixtures("name_of_fixture")
    class Test_Cases:
        ...
3. module: run once for each module. for example, one module may have multiple test classes and test functions
4. package: run once for each package including a __init__.py file
5. session: run once for the entire session, which means all the test cases for the entire pytest execution
    --> use @pytest.fixture(scope="session",autouse=True) to run the fixture automatically without calling it in the test class
    --> if not setting autouse=True in configuration file, then need to pass the name of this fixture before the test case function to call it like the below
    @pytest.mark.usefixtures("name_of_fixture")
    def test_case_1():
        ...

Yield:
1. yield is used within a fixture to define setup and teardown behavior.
    Note: Without using yield, the fixture will always be called before test case execution. Using yield to explicitly define its execution timing.
2. yield is used to pause execution of the test
3. yield can also be used to return a value to the test function
'''

@pytest.fixture(scope="class",autouse=True)
def browser_setup(request):
    """
    Class Scope: 
    To ensure the driver is available and accessible to all methods in the class, 
    If using driver = webdriver.Chrome(), it won't be accessible inside the function in test_xxx, as driver is only a local variablle inside brwoser_setup function
    
    Function scope:
    No need to use request.cls.driver = , use driver = directly
    In test_xxx file, need to pass browser explicitly to the function, e.g. test_xxx(browser_setup)
    """
    request.cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    yield
    request.cls.driver.quit()
