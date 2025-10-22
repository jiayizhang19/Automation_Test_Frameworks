
import os
import sys
import argparse
import configparser
from pytest_run import *
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    # jenkins任务调度使用相对路径导入
    from .before_run import Main
    from .conf.config import PathConfig
except ImportError:
    # pycharm任务调度使用绝对路径导入
    from UI_Automation.before_run import Beforerun
    from UI_Automation.conf.config import PathConfig

from airtest.core.api import *
using("../UI_Automation/common/handlepath.air")
from handlepath import *
# 初始化配置
conf = configparser.ConfigParser()
conf.read(os.path.join(CONFIGDIR, 'conf.ini'), encoding='utf-8')


class Run:
    def __init__(self, case_path=None, include_cases=None, exclude_cases=None, node_name='', exclude_cases_dirs=None,
                 case_level=None, single_send_flag=None, dingding_token=None, bulid_user_name=None, bulid_cron=None, test_plan_name=None):
        pass

    def run(self):
        pass

if __name__ == '__main__':
    # 创建解析器
    parser = argparse.ArgumentParser()

    # ========请仔细查看以下每项传参提示，传参错误会导致运行报错========

    # 默认选择第一个连接的设备，default=0
    parser.add_argument('--driver_no', type=int, default=0)
    # 默认读取conf.ini配置用例目录，可输入目录名称，例如：default=['test_suites_1','test_suites_2',]
    parser.add_argument('--case_path', type=str, nargs='+', default=['test_suites_1','test_suites_2'])
    # 默认指定用例为空，可输入值例如：default=["test_example_1","test_example_2",]，错误示范==>default=['test_example_1.air']
    # parser.add_argument('--include_cases', type=str, nargs='+', default=["test_example_1","test_example_2",])
    parser.add_argument('--include_cases', type=str, nargs='+', default=["test_example_1","test_example_2",])
    # 默认排除用例为空，可输入值例如：default=["test_example_1","test_example_2",]，错误示范==>default=['test_example_1.air']
    parser.add_argument('--exclude_cases', type=str, nargs='+', default=["test_example_1","test_example_2",])
    # 传入jenkins构建节点，默认为空
    parser.add_argument('--node_name', type=str, default='')
    # 默认排除用例目录，可输入值例如：default=['test_suites_1','test_suites_2',]
    parser.add_argument('--exclude_cases_dirs', type=str, nargs='+', default=['test_suites_1','test_suites_2',])
    # 默认用例级别，可输入值例如：default=['P0','P1','P2']，[]执行所有级别用例
    parser.add_argument('--case_level', type=str, nargs='+', default=["P0"])
    # 发送钉钉单个用例报告开关:True、False，默认打开
    parser.add_argument('--single_send_flag', type=str, default='True')
    # 发送钉钉群，默认核心必测群
    parser.add_argument('--dingding_token', type=str, default=None)
    # 传入jenkins任务构建人，默认为空，示例：test
    parser.add_argument('--bulid_user_name', type=str, nargs='?', default='')
    # 传入jenkins任务配置的cron表达式，默认为空，示例：10 10 * * *
    parser.add_argument('--bulid_cron', type=str, nargs='?', default='')
    # 传入jenkins任务名称，默认为空取配置文件
    parser.add_argument('--test_plan_name', type=str, default='')
    # 解析命令行参数
    args = parser.parse_args()

    pytest_case, airtest_case = auto_dispatch_test_files(
        include_case_path=args.case_path, 
        include_case=args.include_cases, 
        exclude_case=args.exclude_cases,
        exclude_case_path=args.exclude_cases_dirs,
        case_level=args.case_level
        )
    
    if pytest_case:
        print(f"pytest run: {pytest_case}")
        case_info = {
            "case_paths": pytest_case,
        }
        message_info = {
            'dingding_token': args.dingding_token,
            'node_name': args.node_name, 
            'single_send_flag': args.single_send_flag,
        }
        os.environ["PYTEST_CASE_INFO"] = json.dumps(case_info)
        os.environ['MESSAGE_INFO'] = json.dumps(message_info)
        pytest_run(
            targets=pytest_case
        )
    if airtest_case:
        # 运行测试
        print(f"airtest run {airtest_case}")
        # x = Run(
        #         case_path=args.case_path, 
                # include_cases=airtest_case,
                # include_cases=args.include_cases, 
                # exclude_cases=args.exclude_cases,
                # node_name=args.node_name, 
                # exclude_cases_dirs=args.exclude_cases_dirs,
                # case_level=args.case_level, 
                # single_send_flag=args.single_send_flag,
                # dingding_token=args.dingding_token, 
                # bulid_user_name=args.bulid_user_name,
                # bulid_cron=args.bulid_cron, 
                # test_plan_name=args.test_plan_name
                # )
        # x.run()

        


