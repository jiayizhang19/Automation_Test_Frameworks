
from airtest.core.api import *
import os
import requests
import time
import json
import pymysql
from datetime import datetime
import random
from concurrent.futures import ThreadPoolExecutor

from airtest.core.android.adb import ADB
device_id = ADB().devices()[0][0]
auto_setup(__file__, devices=[f"Android://127.0.0.1:5037/{device_id}"])

# 设置全局超时时间
ST.FIND_TIMEOUT = 60

# 设置项目路径，用来生成测试报告，不然报告会生成失败，提示图片找不到
ST.PROJECT_ROOT = os.path.abspath('../').replace('\\', '/')


# 调用PO图片元素
# 企业列表元素
using("../../PO/unionList_bfd.air")
from unionList_bfd import *

# 调用公共action
using("../../publicAction.air")
from publicAction import *


# 进入百福得小程序,切换环境后并到登录页
def enter_wx():
    """
    进入微信
    """
    start_time = time.time()
    # -------------解锁屏幕------------------
    wake()
#     unlock()
    # --------------切换输入法-----------------
    switch_input_method_yosemite()

    # --------------关闭微信，并重新打开微信----------
    stop_app("com.tencent.mm")
    start_app("com.tencent.mm")