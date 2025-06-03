# -*- encoding=utf8 -*-
__author__ = "UI自动化"
__title__ = "管理执行用例范围服务"
__desc__ = "专门用于管理执行用例范围，提供指定、排除用例/项目等方法"

import os
import re
import sys
import configparser
import datetime
from datetime import datetime
from airtest.core.api import *
# 加载 handlepath.air 模块
using("../../common/handlepath.air")
from handlepath import *
from  UI_Automation.conf.config import PathConfig
# 初始化配置
conf = configparser.ConfigParser()
conf.read(os.path.join(CONFIGDIR, 'conf.ini'), encoding='utf-8')

class Manage_cases:
    def __init__(self, case_path=None, case_level=None, exclude_cases_dirs=None, include_cases=None, exclude_cases=None, start_time=None):
        """
        初始化 CaseManager
        :param case_path: 用例路径（可以是单个路径或路径列表）
        :param case_level: 指定用例级别（如 P0/P1/P2）
        :param exclude_cases_dirs: 排除的目录列表
        :param include_cases: 包含的用例列表（文件名）
        :param exclude_cases: 排除的用例列表（文件名）
        """
        self.config = eval(conf.get('environment', 'env'))
        # 开始时间作为最后报告汇总执行时间的依据
        self.start_time = start_time if start_time else datetime.now()
        # 项目名称+执行开始时间，作为报告名称标识
        self.run_start_time = str(self.start_time.strftime("%Y-%m-%d_%H-%M-%S_%f"))
        # 获取用例路径
        self.case_path = case_path or eval(conf.get('case', 'case_path'))
        print(f"Manage_cases 文件 case_path获取到用例路径: {self.case_path}, type: {type(self.case_path)}")

        # 处理 case_level，默认值从 CASE_LEVEL 获取
        self.case_level = case_level if case_level else CASE_LEVEL
        print(f"Manage_cases 文件 cases_level指定用例级别: {self.case_level}, type: {type(self.case_level)}")

        # 处理 exclude_cases_dirs，默认为空列表
        self.exclude_cases_dirs = exclude_cases_dirs or []
        print(f"Manage_cases 文件 exclude_cases_dirs排除用例目录: {self.exclude_cases_dirs}, type: {type(self.exclude_cases_dirs)}")

        # 处理 include_cases，支持逗号分隔的字符串转为列表
        if include_cases and isinstance(include_cases, list) and len(include_cases) == 1:
            if isinstance(include_cases[0], str) and (',' in include_cases[0] or '，' in include_cases[0]):
                include_cases = [case.strip() for case in include_cases[0].replace('，', ',').split(',')]
        self.include_cases = include_cases or []
        print(f"Manage_cases 文件 include_cases指定用例: {self.include_cases}, type: {type(self.include_cases)}")

        # 处理 exclude_cases，默认为空列表
        if exclude_cases and isinstance(exclude_cases, list) and len(exclude_cases) == 1:
            if isinstance(exclude_cases[0], str) and (',' in exclude_cases[0] or '，' in exclude_cases[0]):
                # 统一处理为英文逗号，并分割字符串
                exclude_cases = [case.strip() for case in exclude_cases[0].replace('，', ',').split(',')]
        self.exclude_cases = exclude_cases if exclude_cases else []
        print(f"Manage_cases 文件 exclude_cases排除用例: {self.exclude_cases}, type: {type(self.exclude_cases)}")


        # 在case目录下正则匹配case
        self.case_filter = r'^\d*.air$'
        # self.case_filter_sys = r'^sys[a-z_]*_\d*.air$'
        #Emily
        self.case_filter_regex = r'^(sys[a-z_]*_\d*|\d*|user-\d*).air$'

        # 初始化最终用例列表
        self.final_case_list = []
        # 匹配完成后的case目录列表,用来执行用例以及生成报告
        self.case_path_list = []

    def get_all_case(self):
        """
        获取所有用例的绝对路径
        """
        subdirectories = self._get_subdirectories()
        self._process_subdirectories(subdirectories)
        self._filter_cases()

    def _get_subdirectories(self):
        """
        获取所有符合条件的子目录
        """
        subdirectories = set()
        if type(self.case_path) is str:
            self.case_path = [self.case_path]
        for directory in self.case_path:
            for root, dirs, files in os.walk(directory):
                # print(f'root: {root}, dirs: {dirs}, files: {files}')
                for dir_item in dirs:
                    if self._is_valid_directory(root, dir_item):
                        subdirectories.add(os.path.join(root, dir_item))
        # print(f"所有符合条件的子目录: {subdirectories}")
        return sorted(subdirectories)

    def _is_valid_directory(self, root, dir_item):
        """
        检查目录是否符合要求
        """
        full_path = os.path.join(root, dir_item)
        return (dir_item in self.case_level) and \
            not any(exclude_item in full_path for exclude_item in self.exclude_cases_dirs)

    def _process_subdirectories(self, subdirectories):
        """
        遍历子目录，获取用例信息
        """
        for dir_name in subdirectories:
            case_names = self._get_case_names(dir_name)
            for file_name in case_names:
                case_path = os.path.join(dir_name, f"{file_name}.air")
                if os.path.exists(case_path):
                    case_info = {
                        'file_name': file_name,
                        'case_path': case_path,
                        'dir_name':dir_name
                    }
                    self.case_path_list.append(case_info)
                    # self.case_path_list.append(case_path)
        for case in self.case_path_list:
            if self.include_cases and case['file_name'] not in self.include_cases:
                continue
            if self.exclude_cases and case['file_name'] in self.exclude_cases:
                continue
            self.final_case_list.append(self.get_one_case(case['dir_name'], case['file_name']))
        return self.final_case_list,self.case_path_list


    def _get_case_names(self, dir_name):
        """
        获取目录下的用例名称，并尝试排序
        """
        try:
            case_names = {name.split('.')[0] for name in os.listdir(dir_name)}
            # print(f"找到的用例名称为: {case_names}")
            return sorted(case_names, key=lambda x: int(x.split('-')[1]))
        except (IndexError, ValueError):
            print(f"用例排序失败，跳过排序。异常用例列表为: {case_names}")
            return list(case_names)

    def _filter_cases(self):
        """
        根据包含和排除规则过滤用例
        """
        filtered_cases = []
        for case in self.final_case_list:
            if (self.include_cases and case['file_name'] not in self.include_cases) or \
                    (self.exclude_cases and case['file_name'] in self.exclude_cases):
                continue
            filtered_cases.append(case)
        self.final_case_list = filtered_cases

    def get_one_case(self, dir_name, file_name):
        """
                获取单个用例的详细信息
        """
        case_path = os.path.join(dir_name, f"{file_name}.air")
        log_path = os.path.join(dir_name, f"{file_name}.log")
        report_path = os.path.join(dir_name, f"{file_name}.html")
        # report_part_path = os.path.dirname(case_path.replace(BASEDIR, ''))
        relative_report_part_path = os.path.relpath(os.path.dirname(case_path),BASEDIR)
        report_part_path = '\\' + relative_report_part_path
        data= {
            "file_name": file_name.replace('.air', ''),
            "case_path": case_path,
            "log_path": self.config.log_path + report_part_path + '__' + self.run_start_time + '\\'+ file_name,
            "report_path": self.config.report_path + report_part_path + '__' + self.run_start_time + '\\' + file_name + '.log' + '\\log.html',
            'report_part_path': report_part_path
        }
        return data
