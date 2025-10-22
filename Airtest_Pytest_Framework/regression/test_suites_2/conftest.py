"""
Following configurations will only be applied to those test cases under the same folder, to be specific, test_suits_2.
See detailed instructions in airtest_pytest_framework/conftest.py

"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from airtest.core.api import *

using("../../../../common/publicAction.air")
from publicAction import *


@pytest.fixture(scope="session", autouse=True)
def setup_gw(setup_update_overall_reports):
    enter_wx_gw() 

@pytest.fixture(scope="module", autouse=True)
def cleanup_env():
    yield
    return_to_homepage_gw()
    before_login_gw()









