import pytest
import time
import os

"""
You can have conftest.py in different levels within the project. 
Execution order of fixtures depends on:
 - Their scope (session > module > class > function)
 - Their dependency tree (i.e., what depends on what, def setup_airtest_report(setup_bfd))

The request object is used  to pass contextual information about the current test. 
It provides details about the test  being executed, for instance test-related metadata and functionality.
 --> request.module: Refers to the module where the test resides.
 --> request.function: Represents the specific test function being run in the module.
 --> request.cls: Points to the test class where the test function is located.
"""

report_dir = r"D:\..."

@pytest.fixture(scope="session", autouse=True)
def setup_bfd():
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = os.path.join(report_dir,timestamp)
    # your function here
    yield {"report_dir": report_dir}

@pytest.fixture(scope="module", autouse=True)
def cleanup_env():
    yield
    # your function here

@pytest.fixture(scope="module",autouse=True)
def setup_airtest_report(request,setup_bfd, cleanup_env):
    test_file = request.module.__file__
    test_name = os.path.splitext(os.path.basename(test_file))[0]
    report_dir = setup_bfd["report_dir"]
    os.makedirs(report_dir,exist_ok=True)
    log_dir = os.path.join(report_dir,f"{test_name}_log")
    os.makedirs(log_dir,exist_ok=True)
    # your function here
    yield
    # your function here
