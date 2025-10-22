from airtest.core.api import *


using("../../../../common/publicAction.air")
from publicAction import *

using("../../../../common/publicAction_testsuites_1.air")
from publicAction_testsuites_1 import *


def test_example_1():
    login_wx()