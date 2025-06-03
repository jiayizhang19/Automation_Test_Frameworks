# -*- encoding=utf8 -*-
__author__ = "UI自动化_zhaolianyun"
__title__ = "管理发送报告消息的服务"
__desc__ = "专门用于管理报告发送，提供发送整体或单条包到钉钉等方法"

import configparser
import logging
# 设置日志级别
logging.basicConfig(level=logging.INFO)
from datetime import datetime
import requests
from airtest.core.api import *
from  UI_Automation.conf.config import PathConfig
from UI_Automation.utils.time_manager.time_helper import TimeHelper
#引用DatabaseHelper
from UI_Automation.utils.db.helper import *
from UI_Automation.utils.db.queries import *

#引用case_manager
from UI_Automation.utils.case_manager.test_case_manager import Manage_cases

using("../../common/handlepath.air")
from handlepath import *

# 初始化配置
conf = configparser.ConfigParser()
conf.read(os.path.join(CONFIGDIR, 'conf.ini'), encoding='utf-8')

class Message_manager:
    def __init__(self,manage_cases:Manage_cases,node_name=None,dingding_token=None,start_time=None, single_send_flag=None):
        #实例化Manage_cases,获取case_path,case_level,project_name
        self.manage_cases = manage_cases
        self.dbHelper = DatabaseHelper()
        self.timeHelper = TimeHelper()
        self.config = eval(conf.get('environment', 'env'))
        self.json_headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        # 获取节点名称
        self.node_name = node_name
        # 未指定级别，则取配置handlepath中所有的case级别
        self.case_level = self.manage_cases.case_level if self.manage_cases else self.manage_cases.CASE_LEVEL
       # 获取每次发送报告条数
        self.base_num = eval(conf.get('send_msg', 'base_num'))
       # 获取是否发送完整报告
        self.send_flag = eval(conf.get('send_msg', 'send_flag'))
        #获取发送钉钉单条消息
        self.single_send_flag = single_send_flag or eval(conf.get('send_msg', 'single_send_flag'))
        logging.info(f"jenkins调试====>Message_manager.single_send_flag数据类型转换前====>钉钉单条报告发送开关（True=开启，False=关闭）为: {self.single_send_flag}, type: {type(self.single_send_flag)}")
        # 获取钉钉机器人token
        self.dingding_token = dingding_token or conf.get('send_msg', 'dingding_token')
        # 获取单条报告默认钉钉机器人token
        self.single_dingding_token = self.dingding_token if self.dingding_token != conf.get('send_msg', 'single_dingding_token') else conf.get('send_msg', 'single_dingding_token')
        # 获取整体报告默认钉钉机器人token
        self.total_dingding_token = self.dingding_token if self.dingding_token != conf.get('send_msg', 'total_dingding_token') else conf.get('send_msg', 'total_dingding_token')
        #get_current_time()返回的是字符串
        self.start_time = start_time if  start_time else self.timeHelper.get_current_time()
        # 报告保留数量
        self.save_dirs_num = eval(conf.get('report', 'number'))
        # 获取钉钉机器人是否发送单条执行结果(jenkins传入为str类型，转换为bool类型，转换失败默认为True)
        temp_single_send_flag = single_send_flag or eval(conf.get('send_msg', 'single_send_flag'))
        if not isinstance(temp_single_send_flag, bool):
            try:
                self.single_send_flag = eval(str(temp_single_send_flag).capitalize())
                print(f"jenkins调试====>Message_manager.single_send_flag数据类型转换后====>钉钉单条报告发送开关（True=开启，False=关闭）为: {self.single_send_flag}, type: {type(self.single_send_flag)}")
            except (ValueError, SyntaxError):
                self.single_send_flag = True
        else:
            self.single_send_flag = temp_single_send_flag
            print(f"jenkins调试====>Message_manager.single_send_flag无需转换数据类型====>钉钉单条报告发送开关（True=开启，False=关闭）为: {self.single_send_flag}, type: {type(self.single_send_flag)}")
    # 业务方法：发动钉钉消息-整体报告
    def send_all_result(self, result):
        """
        将整体报告，发送执行结果到钉钉群，每self.base_num个用例发送一次，并最总汇总用例条数
        """
        db_helper = DatabaseHelper('mini_pro_db')
        """根据testreportid查询整体用例数"""
        self.all_case_num = db_helper.find_one(SELECT_ALL_CASE_NUM, self.testreportid)['count(*)']

        """根据testreportid查询成功用例总数"""
        self.pass_case_num = db_helper.find_one(SELECT_PASS_CASE_NUM, self.testreportid)['count(*)']

        """根据testreportid查询失败用例总数"""
        self.fail_case_num = db_helper.find_one(SELECT_FAIL_CASE_NUM, self.testreportid)['count(*)']

        """根据testreportid查询失败用例list列表"""
        fail_result = db_helper.find_all(SELECT_FAIL_CASE_LIST, self.testreportid)
        self.fail_case_id_list = [result['testid'] for result in fail_result if 'testid' in result]
        self.fail_case_id = ','.join(self.fail_case_id_list)

        """根据testreportid查询未生成报告用例总数"""
        self.unknown_case_num = db_helper.find_one(SELECT_UNKNOWN_CASE_NUM, self.testreportid)['count(*)']

        """成功率"""
        self.success_rate = str(round(float(self.pass_case_num) / float(self.all_case_num) * 100, 2)) + '%'

        """获取test_plan_id"""
        self.test_plan_id = self.testreportid
        title = "小程序-最终报告"
        #格式化时间字符串
        self.formatted_start_time = self.timeHelper.format_time(self.start_time)
        #执行结束时间，返回的就是字符串
        end_time = self.timeHelper.get_current_time()
        # 将字符串转换为 datetime 对象
        end_time_obj = self.timeHelper.parse_time(end_time)
        #计算时间差，传入的是2个时间对象，返回时间差对象
        time_diff = self.timeHelper.calculate_time_difference(self.start_time, end_time_obj)
        # 将时间差对象格式化为易读的字符串
        self.time_diff_seconds = self.timeHelper.format_timedelta(time_diff)
        # self.time_diff_seconds = str(time_diff)
        # print(f'self.time_diff_seconds: {self.time_diff_seconds}')
        print(f'==================== self.project_name={self.project_name}, self.test_plan_name is {self.test_plan_name}, self.config.__name__ is {self.config.__name__}, self.all_case_num is {str(self.all_case_num)}')
        print(f'self.pass_case_num is {str(self.pass_case_num)}, self.fail_case_num is {str(self.fail_case_num)}, self.fail_case_id is {self.fail_case_id}, self.unknown_case_num is {str(self.unknown_case_num)}')
        print(f'self.success_rate is {str(self.success_rate)}, self.formatted_start_time is {self.formatted_start_time}, end_time is {end_time}, self.time_diff_seconds is {self.time_diff_seconds}')
        print(f'self.node_name is {self.node_name}, self.test_plan_id is {self.test_plan_id} ====================')
        text = '##  UI自动化测试报告_小程序' + '\n' + \
               '####  项目名称：' + self.project_name + '\n' + \
               '####  测试计划：' + self.test_plan_name + '\n' + \
               '####  执行人员：' + self.config.__name__ + '\n' + \
               '####  用例总数：' + str(self.all_case_num) + '\n' + \
               '####  成功用例数：<font color="green">' + str(self.pass_case_num) + '</font>\n' + \
               '####  失败用例数：<font color="red">' + str(self.fail_case_num) + '\n' +\
               '>###### 失败用例汇总：' + self.fail_case_id + '\n' + \
               '####  未生成文件数：' + str(self.unknown_case_num) + '\n' + \
               '####  通过率：' + str(self.success_rate) + '\n' + \
               '####  开始时间：' + self.formatted_start_time + '\n' + \
               '####  结束时间：' + end_time + '\n' + \
               '####  执行时长：' + self.time_diff_seconds + '\n' + \
               '#### 当前执行节点：<font color="red">' + self.node_name + '</font>\n' + \
               '####  详细信息：<font color="blue">[测试报告详情](http://10.55.10.3:8000/system/reports_case/{})</font>'.format(
                   self.test_plan_id) + '\n'
        if self.send_flag:
            print(f"发送钉钉消息====>发送汇总报告")
            print(f'======== text is {text} ========')
            self.send_to_dingding(self.total_dingding_token, title, text)

        # case_level = '、'.join(self.case_level)
        #
        # # 生成最终报告
        # text = '##  最终报告：' + project_name + '\n' + \
        #        '####  用例级别：' + case_level + '\n' + \
        #        '####  报告目录：<font color="blue">' + self.config.report_path + '</font>\n' + \
        #        '####  报告标识：[' + self.run_start_time + ']\n' + \
        #        '####  开始时间：' + self.start_time.strftime("%Y-%m-%d %H:%M:%S") + '\n' + \
        #        '####  结束时间：' + end_time.strftime("%Y-%m-%d %H:%M:%S") + '\n' + \
        #        '####  执行时长：' + self.transform_diff_time(time_diff_seconds) + '\n' + \
        #        '####  当前执行节点：<font color="red">' + self.node_name + '</font>\n' + \
        #        '######  台式机节点：slave1\n' + \
        #        '######    远程ip：10.55.37.176，账密：admin、Aa@123456789\n' + \
        #        '######  笔记本节点：slave2\n' + \
        #        '######    远程ip：10.55.10.3，账密：admin、Df@2021!\n' + \
        #        '####  执行人员：' + self.config.__name__ + '\n'
        #
        # # 执行成功、失败用例汇总
        # fail_cases = {}
        # pass_cases = {}
        # # 发送整体报告 - 数量准备
        # fail_num = 0
        # pass_num = 0
        # dic_report_num_all = {i: 0 for i in self.case_level}
        # dic_report_num_fail = {i: 0 for i in self.case_level}
        # dic_report_num_pass = {i: 0 for i in self.case_level}
        # # 每n条发送一次
        # base = self.base_num
        # # 如果有多份报告，则给标识
        # if base < len(result):
        #     text = text + '####  报告标识：[' + self.run_start_time + '] - 第[' + str(1) + ']份报告\n'
        # text = text + '####  报告内容：\n'
        # for index, one_report in enumerate(result):
        #     # 处理case条数汇总：数量、成功/失败的case_id
        #     level = one_report['report_part_path'].split('\\')[-1]
        #     dic_report_num_all[level] += 1
        #     if one_report['case_result'].find('通过') == -1:
        #         fail_num += 1
        #         dic_report_num_fail[level] += 1
        #         if '\\'.join(one_report['report_part_path'].split('\\')[1:3]) not in fail_cases:
        #             fail_cases['\\'.join(one_report['report_part_path'].split('\\')[1:3])] = []
        #         fail_cases['\\'.join(one_report['report_part_path'].split('\\')[1:3])].append(one_report["case_id"])
        #     else:
        #         pass_num += 1
        #         dic_report_num_pass[level] += 1
        #         if '\\'.join(one_report['report_part_path'].split('\\')[1:3]) not in pass_cases:
        #             pass_cases['\\'.join(one_report['report_part_path'].split('\\')[1:3])] = []
        #         pass_cases['\\'.join(one_report['report_part_path'].split('\\')[1:3])].append(one_report["case_id"])
        #
        #     # 发送文案处理
        #     current_text = '##### ' + str(one_report["case_id"]) + '：' + one_report["case_result"] + '\n' + \
        #                    '> ###### 用例路径： ' + one_report["report_part_path"] + '\n' + \
        #                    '> ###### 用例场景： ' + one_report["case_name"] + '\n' + \
        #                    '> ###### 开始时间：' + str(one_report["start_time"]) + '\n' + \
        #                    '> ###### 结束时间：' + str(one_report["end_time"]) + '\n' + \
        #                    '> ###### 执行耗时：' + self.transform_diff_time(one_report["diff_time"]) + '\n' + \
        #                    '> ###### 报告地址：' + one_report['report_path'] + '\n'
        #     text = text + current_text + '\n'
        #
        #     # 当前是最后一条，拼接上汇总信息后，发送钉钉消息
        #     if index + 1 == len(result):
        #         result_count = '总计{}条，通过<font color="green">{}</font>条，' \
        #                        '失败<font color="red">{}</font>条，' \
        #                        '通过率<font color="green">{:.2f}%</font>'.format(len(result), pass_num, fail_num,
        #                                                                       0.00 if len(
        #                                                                           result) == 0 else pass_num / len(
        #                                                                           result) * 100)
        #         text = text + '####  报告汇总：' + result_count + '\n'
        #         # 处理详细报告
        #         result_item = {i: "" for i in self.case_level}
        #         for level in self.case_level:
        #             if dic_report_num_all[level] > 0:
        #                 result_item[level] = '{}总计{}条，通过<font color="green">{}</font>条，' \
        #                                      '失败<font color="red">{}</font>条，' \
        #                                      '通过率<font color="green">{:.2f}%</font>'.format(level,
        #                                                                                     dic_report_num_all[level],
        #                                                                                     dic_report_num_pass[level],
        #                                                                                     dic_report_num_fail[level],
        #                                                                                     dic_report_num_pass[level] /
        #                                                                                     dic_report_num_all[
        #                                                                                         level] * 100)
        #             else:
        #                 result_item[level] = '{}总计0条，通过<font color="green">0</font>条，失败<font color="red">0</font>条，' \
        #                                      '通过率<font color="green">0.00%</font>'.format(level)
        #             current_result_text = '> ###### 结果明细： ' + result_item[level] + '\n'
        #             text = text + current_result_text + '\n'
        #         self.send_to_dingding(self.total_dingding_token, title, text)
        #     elif (index + 1) % base == 0:
        #         # 每base条（当前不是最后条），发送一次消息，并将text重新赋值
        #         self.send_to_dingding(self.total_dingding_token, title, text)
        #         text = '####  报告标识：[' + self.run_start_time + '] - 第[' + str((index + 1) // base + 1) + ']份报告\n' + '####  报告内容：\n'
        # # 清空内容后，发送汇总的成功、失败用例case_id
        # text = ""
        # for key, value in pass_cases.items():
        #     text = text + '####  <font color="green">执行成功用例：</font>' + '\n' + '> ###### 用例目录：' + key + '\n' + '> ###### 用例汇总：' + ','.join(value) + '\n'
        # for key, value in fail_cases.items():
        #     text = text + '####  <font color="red">执行失败用例：</font>' + '\n' + '> ###### 用例目录：' + key + '\n' + '> ###### 用例汇总：' + ','.join(value) + '\n'
        # self.send_to_dingding(self.single_dingding_token, title, text)

    # 业务方法：发送单条钉钉消息
    def send_result(self, file_name, case_result, case_name, report_part_path):
        """
        发送单条用例执行结果到钉钉群
        """
        # 获取用例执行目录
        case_path = [self.manage_cases.case_path] if type(
            self.manage_cases.case_path) is str else self.manage_cases.case_path
        print(f"send_all_result 文件 case_path指定用例路径: {case_path}, type: {type(case_path)}")
        project_names = [i.replace(BASEDIR, '') for i in case_path]
        print(f"project names are {project_names}")
        if project_names == [''] or not project_names:
            project_name = '、'.join([item for item in CASEDIR_MAPPING.values() if item.endswith('项目')])
        else:
            project_names = [i.replace(BASEDIR, '') for i in case_path]
            project_names = [i.split('\\') for i in project_names]
            project_name = '、'.join([CASEDIR_MAPPING[item[1]] if len(item) == 2 else '_'.join(
                [CASEDIR_MAPPING[item[1]], CASEDIR_MAPPING[item[2]]]) for item in project_names])
        self.project_name = project_name
        print(f"self.project_name is {self.project_name}")
        # 截取第一个 '_' 前面的部分
        project = project_name.split('_')[0]
        # print(f'self.project_name,: {self.project_name},self.project = {self.project},file_name:{file_name}')
        db_helper = DatabaseHelper('mini_pro_db')
        """根据file_name查询report_url 和testreportid """
        # 组合参数为一个元组
        params = (project, file_name)
        print(f"params is {params}")
        report_url = db_helper.find_one(SELECT_LATEST_REPORT_INFO, params).get('report_url')
        self.testreportid = db_helper.find_one(SELECT_LATEST_REPORT_INFO, params).get('testreportid')
        print(f"self.testreportid is {self.testreportid}")
        """根据testreportid查询test_plan_id 和test_plan_name """
        self.test_plan_name = db_helper.find_one(SELECT_REPORT_CASE_INFO, self.testreportid).get('testplanname')
        # print(f'self.report_url:{self.report_url},self.testreportid={self.testreportid},self.test_plan_name={self.test_plan_name}')

        # title = "【%s】小程序自动化执行结果" %CASEDIR_MAPPING[report_part_path.split('\\')[1]]
        normalized_path = os.path.normpath(report_part_path)
        if not normalized_path.startswith(os.sep):
            normalized_path += os.sep
        report_part_path = normalized_path
        title = "【%s】小程序自动化执行结果" %CASEDIR_MAPPING[report_part_path.split(os.sep)[1]]
        text = '####  ' + str(file_name) + ' ： ' + str(case_result) + '\n' \
               + '> ###### 用例路径： ' + str(report_part_path) + '\n' \
               + '> ###### Case Name: ' + str(case_name) + '\n' \
               + '> ###### 当前时间： ' + (str(datetime.now())).split('.')[0] + '\n' \
               + '> ###### 查看报告：<font color="blue">[报告详情]({})</font>'.format(report_url) + '\n'
        if self.single_send_flag:
            print(f"**************发送单条用例结果到钉钉群**************开关=True: {self.single_send_flag}")
            if self.single_dingding_token != "42765bcec4dbfa0af13a0c115804e6a97461ceae5c5b732508cd5681ad487bf5":
                """若单条报告设置的token的值不是核心必测群的token,则发送到设置的token"""
                self.send_to_dingding(self.single_dingding_token, title, text, True)
            else:
                """若单条报告的token值是核心必测群，则发送到备用token即小程序小程序自动化用例执行结果群"""
                backup_token = "22ebe571cf8b5b82da497827d848d25cdc9ca0a3fc42b62b9caad583f3ffd06f"
                self.send_to_dingding(backup_token, title, text, True)

    # 基础方法：发送钉钉消息，失败转发
    def send_to_dingding(self, dingding_token, title, text, at_all=False):
        """
        发送失败时进行转发
        """
        # DINGDING_TOKEN_MAPPING来源：/UI_Automation/common/handlepath.air；用于映射群名称
        dingding_name = '个人测试群' if dingding_token not in DINGDING_TOKEN_MAPPING else DINGDING_TOKEN_MAPPING[dingding_token]
        errmsg = self.send_to_dingding_base(dingding_token, title, text, at_all)
        print('群：【%s】，机器人【%s】钉钉消息发送结果====>%s' % (dingding_name, dingding_token, errmsg))
        if errmsg != 'ok':
            print('群：【%s】，机器人【%s】钉钉消息发送结果====>%s' % (dingding_name,dingding_token, '机器人发送失败'))
            text = '######  群：【%s】，机器人【%s】发送失败' % (dingding_name, dingding_token) + '，转入默认测试群发送消息' + '\n' + text + '\n'
            errmsg = self.send_to_dingding_base(DINGDING_TOKEN_MAPPING['默认测试群'], title, text, at_all)
            print('群：【%s】，机器人【%s】钉钉消息发送结果====>%s' % ('默认测试群', DINGDING_TOKEN_MAPPING['默认测试群'], errmsg))

    # 基础方法：发送钉钉消息
    def send_to_dingding_base(self, dingding_index, title, text, at_all=False):
        """
        基础发送钉钉消息方法
        """
        url = "https://oapi.dingtalk.com/robot/send?access_token=%s" % dingding_index
        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            }
        }

        if '失败' in text and at_all:
            message['at'] = {
                "isAtAll": True
            }
        res = requests.post(url, json=message, headers=self.json_headers)
        return res.json().get('errmsg')
