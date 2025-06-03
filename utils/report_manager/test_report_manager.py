# -*- encoding=utf8 -*-
__author__ = "UI自动化"
__title__ = "管理执行用例生成报告的，发送消息的服务"
__desc__ = "专门用于管理报告的方法，提供单条报告、整体报告，发送单条报告消息，整体报告消息的方法"

import configparser
import os
import re
import shutil
import time
import zipfile
from datetime import datetime
import paramiko
import psutil

from  UI_Automation.conf.config import PathConfig
from airtest.core.api import *
#引用DatabaseHelper
from UI_Automation.utils.db.helper import *
from UI_Automation.utils.db.queries import *
#引用case_manager包
from UI_Automation.utils.case_manager.test_case_manager import Manage_cases
from UI_Automation.utils.time_manager.time_helper import  *

# 加载 handlepath.air 模块
using("../../common/handlepath.air")
from handlepath import *

#导入数据库操作
using('../../common/connectdb.air')
from connectdb import DB

# 初始化配置
conf = configparser.ConfigParser()
conf.read(os.path.join(CONFIGDIR, 'conf.ini'), encoding='utf-8')


class ReportManager:
    def __init__(self,manage_cases:Manage_cases,bulid_user_name=None, test_plan_name=None, test_plan_id=None,final_case_list=None, start_time=None):
        self.config = eval(conf.get('environment', 'env'))
        #实例化manage_cases
        self.manage_cases = manage_cases
        #实例化TimeHelper
        self.timeHelper = TimeHelper()
        # 获取manage_cases的bulid_user_name
        self.bulid_user_name = bulid_user_name
        # 开始时间作为最后报告汇总执行时间的依据
        # self.start_time = start_time if start_time else datetime.now()
        self.start_time = start_time if  start_time else self.timeHelper.get_current_time()
        print(f'self.start_time 的type:{type(self.start_time)},{self.start_time}')
        # 项目名称+执行开始时间，作为报告名称标识
        self.run_start_time = str(self.start_time.strftime("%Y-%m-%d_%H-%M-%S_%f"))
        # 报告保留数量
        self.save_dirs_num = eval(conf.get('report', 'number'))
        # 报告信息是否写入数据库
        self.write_db_flag = eval(conf.get('write_db', 'write_db_flag'))
        # 是否发送完整报告
        self.send_flag = eval(conf.get('send_msg', 'send_flag'))
        self.case_path = self.manage_cases.case_path
        self.env_value = conf.get('environment', 'env')
        # 测试计划id
        self.test_plan_id = test_plan_id
        # 测试计划用例列表
        self.final_case_list = final_case_list if final_case_list is not None else self.manage_cases.final_case_list
        self.test_plan_name = test_plan_name
        self.test_report_id = None

    # 基础方法：准备报告目录
    def prepare_dirs(self, dirs_path, save_dirs_num=3):
        """
        准备报告、日志目录：创建指定目录，并删除多余的，最多保留save_dirs_num个
        :return:
        """
        # 每个级别的报告保留最新的save_dirs_num个
        for item in self.manage_cases.case_level:
            all_projects_dirs = os.listdir(dirs_path)
            all_dirs = []
            for item_dir in all_projects_dirs:
                if item_dir.startswith(item):
                    all_dirs.append(item_dir)
            all_dirs.sort()
            all_dirs_num = len(all_dirs)
            if all_dirs_num > self.save_dirs_num:
                for index, item_dir in enumerate(all_dirs[0:all_dirs_num - self.save_dirs_num]):
                    item_dir_path = os.path.join(dirs_path, item_dir)
                    if os.path.isdir(item_dir_path):
                        shutil.rmtree(item_dir_path, ignore_errors=True)

    # 基础方法：准备报告目录、日志目录
    def prepare_report_dir(self,report_part_path):
        """
        准备报告目录、日志目录：创建指定目录（用例级别P0/P1 + self.run_start_time），并删除多余的，最多保留save_dirs_num个
        :return:
        """

        report_path = os.path.join(self.config.report_path + report_part_path + '__' + self.run_start_time)
        # print("开始准备报告目录====>" + report_path)
        if not os.path.exists(report_path):
            os.makedirs(report_path, exist_ok=True)
            self.prepare_dirs(os.path.dirname(report_path), self.save_dirs_num)
        # print("完成准备报告目录")
        log_path = os.path.join(self.config.log_path + report_part_path + '__' + self.run_start_time)
        # print("开始准备日志目录====>" + log_path)
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
            self.prepare_dirs(os.path.dirname(log_path), self.save_dirs_num)
        # print("完成准备日志目录")

    # 业务方法：提取所有执行的用例报告内容
    def get_final_report(self):
        """
        生成最终报告，根据当前所有报告生成的聚合报告，并发送钉钉
        """
        result = []
        for case in self.manage_cases.final_case_list:
            result.append(self.get_one_report(case['case_path'], case['file_name']))
        return result

    #
    def process_report(self):
        """
        将get_final_report代码拆解出来
        根据开关状态处理测试报告
        1）更新测试报告数据
        2）发送测试报告结果
        :param result: 测试结果数据
        """
        # 如果写入数据库开关开启，则更新测试报告任务数据
        if self.write_db_flag:
            self.update_report_task()

    # 业务方法：提取单条用例报告内容
    def get_one_report(self, case_path=None, file_name=None):
        """
        获取单个报告信息：用例名称、用例路径、用例日志路径、用例报告路径、用例执行结果，用例执行时间，用例执行人
        组装场景：执行失败、执行通过、未生成报告
        :param case_path:
        :param file_name:
        :return:报告内容组装成字典返回
        """
        # case_path 获取到的是到.air目录，处理为父级目录，再获取用例
        #Emily case_path 来源于case_path_list
        case = self.manage_cases.get_one_case(os.path.dirname(case_path), file_name)
        report_path = case['report_path']
        report_part_path = case['report_part_path']
        case_id = case['file_name']
        case_result = '失败'
        run_name = self.config.__name__  # 获取执行人
        print(f"report_path: {report_path}")
        try:
            with open(report_path, 'rb') as file:
                data = file.read().decode('utf-8', 'ignore').replace(u'\xa9', u'')
                case_result = re.findall(r"test_result.*?,", data)[0]  # 匹配执行结果
                run_start = re.findall("run_start.*?,", data)[0].split(' ')[1].split('.')[0]  # 匹配开始时间
                run_end = re.findall("run_end.*?,", data)[0].split(' ')[1].split('.')[0]  # 匹配结束时间
                case_name = re.findall('class="desc-content">.*?</div>', data)[0].split('>')[1].split('<')[0]
                #case编写人
                case_writer = re.findall(r'<span lang="en">Author:</span>(.*?)</div>', data)[0]
                if 'true' in case_result:
                    case_result = '<font color="green">执行通过</font>'
                else:
                    case_result = '<font color="red">执行失败</font>'
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(run_start)))
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(run_end)))
                print(report_part_path + '	' + case_id + '	' + case_name + '	' + case_result + '	' +
                      start_time + '	' + end_time + '	' + run_name)

        except IOError:
            print(report_path + '	' + report_part_path + '	' + case_id + '	无	文件不存在	无	无	' + run_name)
            one_report = {
                "report_path": '无',
                "report_part_path": report_part_path,
                "case_id": case_id,
                "case_name": '无',
                "case_result": '<font color="red">未生成报告</font>',
                "start_time": '无',
                "end_time": '无',
                "diff_time": 0,
                "case_writer": '无',
                "run_name": run_name
            }
            return one_report
        else:
            if file_name is not None:
                one_report = {
                    "report_path": report_path,
                    "report_part_path": report_part_path,
                    "case_id": case_id,
                    "case_name": case_name,
                    "case_result": case_result,
                    "start_time": start_time,
                    "end_time": end_time,
                    "case_writer": case_writer,
                    "diff_time": int(run_end)-int(run_start),
                    "run_name": run_name
                }
                return one_report


    '''更新数据库测试报告任务信息'''
    def update_report_task(self):
        # 格式化时间
        end_time = self.timeHelper.get_current_time()
        # 获取执行人信息
        execute_user = self._get_execute_user()
        print(f"最终执行人: {execute_user}")
        # 格式化时间字符串
        # 将字符串转换为 datetime 对象
        end_datetime = self.timeHelper.parse_time(end_time)
        # 计算时间差，传入的是2个时间对象，返回时间差对象
        extime_diff = self.timeHelper.calculate_time_difference(self.start_time, end_datetime)
        # 将时间差对象格式化为易读的字符串
        diff_execute_time = self.timeHelper.format_timedelta(extime_diff)
        print(f'end_time:{end_time},update_report_task的self.execute_time:{diff_execute_time}')
        print(f'self.test_report_id: {self.test_report_id}')
        try:
            db_helper = DatabaseHelper('mini_pro_db')
            # 根据执行计划id更新执行计划状态
            # 执行 SQL 语句
            result = db_helper.execute_update(UPDATE_EXECUTE_TASK,(end_time,end_time,diff_execute_time,self.test_plan_id))# result=1
            if result is not None and result > 0:
                print("mini_test_report-SQL 更新成功")
            elif result is not None and result == 0:
                print("mini_test_report-SQL 未进行更新")
            else:
                print("mini_test_report-SQL 更新失败")
        except Exception as e:
            print(f"mini_test_report-SQL 执行时发生错误: {e}")
    """更新单条case信息到数据库"""
    def update_report_data(self,case,one_report):
        ftp_report_html = one_report['report_path'].replace(self.config.report_path, '')
        # print("本地用例报告地址->html："+ ftp_report_html)
        if self.write_db_flag:
            try:
                print("根据当前执行人和执行状态=0的最新的报告id，去查用例报告表以及case名称+所属项目，来查询更新该条用例的最终执行结果字段")
                #获取用例testid:user-116-2
                test_id=one_report['case_id']
                #获取执行时间，执行时长，执行状态，更新时间
                start_time=one_report['start_time']
                # print('用例执行开始时间:',start_time)
                end_time=one_report['end_time']
                # print('用例执行结束时间:',end_time)
                execute_time=self.timeHelper.transform_diff_time(one_report['diff_time'])
                print('update_report_data用例执行时长:',execute_time)

                # 根据 case_result 设置 status
                if '通过' in one_report['case_result']:
                    status = 2
                elif '失败' in one_report['case_result']:
                    status = 1
                elif '未生成报告' in one_report['case_result']:
                    status = 3
                else:
                    status = 4
                # print('用例报告执行状态:', status)
                # 更新时间
                update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # print('用例报告更新时间:', update_at)
                # 获取项目名
                pre_project_name = (one_report['report_path'].replace(self.config.report_path, '')).split("\\")[1]
                # 映射中文项目名称
                project_name = CASEDIR_MAPPING.get(pre_project_name)
                # 远程服务器用例报告路径url
                ftp_url = f'https://tep.dongfangfuli.com/file/tep-minipro-web/upload/{self.start_time.strftime("%Y-%m-%d")}'
                report_url = (ftp_url + ftp_report_html).replace('\\', '/')
                print("远程服务器用例报告可直接访问url为:", report_url)
                print("更新用例报告id:", self.test_report_id)
                print(
                    f"test id: {test_id}", 
                    f", project_name: {project_name}", 
                    f", start_time: {start_time}",
                    f",end_time: {end_time}",
                    f",execute_time: {execute_time}",
                    f",status: {status}",
                    f",update_at: {update_at}",
                    f",report_url: {report_url}"
                    )
                db_helper = DatabaseHelper('mini_pro_db')
                print("更新的用例报告信息sql:", UPDATE_EXECUTE_TASK_CASE)
                try:
                    # 执行 SQL 语句
                    result = db_helper.execute_update(UPDATE_EXECUTE_TASK_CASE,(self.test_report_id,test_id,project_name,start_time,end_time,execute_time,status,update_at,report_url))  # result=1
                    if result is not None and result > 0:
                        print("mini_test_report_case-SQL 更新成功")
                    elif result is not None and result == 0:
                        print("mini_test_report_case-SQL 未进行更新")
                    else:
                        print("mini_test_report_case-SQL 更新失败")
                except Exception as e:
                    print(f"mini_test_report_case-SQL 执行时发生错误: {e}")
            except Exception as e:
                print(f"更新单条case报告出错啦: {e}")

    """上传单条报告到远程服务器"""
    def upload_report(self,one_report):
        ftp_report_path_full = one_report['report_path'].replace('\\log.html', '')
        # print("本地用例报告地址->全路径：",ftp_report_path_full)
        ftp_report_path = one_report['report_path'].replace(self.config.report_path, '').replace('\\log.html','')
        # print("解析传入远程服务器的报告地址："+ ftp_report_path)
        ftp_report_html = one_report['report_path'].replace(self.config.report_path, '')
        # print("本地用例报告地址->html："+ self.ftp_report_html)
        # ftp配置参数
        server_address = "10.8.101.54"
        server_port = 22
        username = "sdet"
        password = "Sdettep2020!"
        #以上是run_case里面的代码
        # 构建远程目录路径
        remote_root_dir = f"/data/tep/ftpfile/tep-minipro-web/upload/{self.start_time.strftime('%Y-%m-%d')}"
        # print("远程目录路径：", remote_root_dir)
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        zip_file_name = None  # 初始化zip_file_name
        remote_zip_path = None  # 初始化remote_zip_path
        try:
            # 连接到服务器
            ssh.connect(server_address, port=server_port, username=username, password=password)
            # print("连接服务器成功")
            # 创建SFTP客户端
            sftp = ssh.open_sftp()
            # print("创建SFTP客户端成功")
            # 检查并创建远程目录
            try:
                sftp.stat(remote_root_dir)
                # print(f"远程目录 {remote_root_dir} 已存在，无需创建")
            except FileNotFoundError:
                try:
                    sftp.mkdir(remote_root_dir)
                    # print(f"远程目录 {remote_root_dir} 创建成功")
                except IOError as e:
                    if 'Failure' in str(e):
                        print(f"忽略错误: 目录{remote_root_dir}已存在")
                    else:
                        raise
            # 解析report_path,用于创建远程目录
            ftp_parts = ftp_report_path.split('\\')
            current_remote_dir = remote_root_dir
            for part in ftp_parts:
                # 确保目录存在，不存在则创建
                if part:
                    current_remote_dir = os.path.join(current_remote_dir, part).replace('\\', '/')
                    # print(f"检查远程目录是否存在，检查目录为： {current_remote_dir} ")
                    try:
                        sftp.stat(current_remote_dir)
                        # print(f"远程目录 {current_remote_dir} 已存在，无需创建")
                    except FileNotFoundError:
                        sftp.mkdir(current_remote_dir)
                        # print(f"远程目录 {current_remote_dir} 创建成功")
            final_remote_dir = current_remote_dir
            # print(f'最终上传压缩包远程目录为: {final_remote_dir}')
            # 打包压缩报告文件
            zip_file_name = os.path.basename(ftp_report_path_full).replace('.log', '.zip')
            with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(ftp_report_path_full):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, ftp_report_path_full)
                        zipf.write(file_path, arcname)
            # 上传压缩文件
            remote_zip_path = os.path.join(final_remote_dir, zip_file_name).replace('\\', '/')
            sftp.put(zip_file_name, remote_zip_path)
            print(f'上传压缩包成功，远程路径为： {remote_zip_path}，远程文件名为： {zip_file_name}')
            # 解压上传的ZIP包
            command = f'unzip -o {remote_zip_path} -d {final_remote_dir}'
            stdin, stdout, stderr = ssh.exec_command(command)
            # 等待解压命令完成
            exit_status = stdout.channel.recv_exit_status()
            # 检查解压是否成功
            if exit_status == 0:
                # 解压成功，删除远程ZIP包
                sftp.remove(remote_zip_path)
                print(f'解压成功，远程ZIP包已删除')
            else:
                # 解压失败，打印错误信息
                error_output = stderr.read().decode('utf-8')
                print(f'解压失败: {error_output}')
        except Exception as e:
            print(f'>>: {e}')
        finally:
            # 关闭连接
            if 'sftp' in locals():
                sftp.close()
                # print('SFTP连接已关闭')
            if 'ssh' in locals():
                ssh.close()
                # print('SSH连接已关闭')
            # 删除本地的压缩文件
            if zip_file_name:
                os.remove(zip_file_name)
                print(f'本地压缩包文件删除成功,压缩包名称为： {zip_file_name} ')

    """将当前测试任务插入入数据库，将预执行测试用例插入数据库，后续直接更新执行结果"""
    def initialize_test_report_and_cases(self):
        if not self.write_db_flag:
            print("数据库写入标志未开启，跳过初始化数据。")
            return
        try:
            print("++++++++++开始初始化数据++++++")
            db_helper = DatabaseHelper('mini_pro_db')
            # 获取执行人信息
            execute_user = self._get_execute_user()
            print(f"最终执行人: {execute_user}")

            # 获取测试计划名称
            test_plan_name = self.test_plan_name or f"【个人】{execute_user}执行计划报告"
            print(f"最终测试计划名称: {test_plan_name}")

            # 获取时间字段
            start_time = self.start_time
            update_at = self.start_time

            # 插入测试任务插入数据库表
            report_id = self._insert_test_report(db_helper, execute_user, test_plan_name, start_time, update_at)
            if report_id is None:
                print("测试报告初始化失败，终止后续操作。")
                return
            self.test_report_id = report_id
            self.test_plan_id = report_id
            # 将预执行测试用例插入数据库待后续更新测试结果
            self._initialize_test_cases(db_helper, report_id)
            print("++++++++++初始化数据结束++++++")
        except Exception as e:
            print(f"初始化数据时发生错误: {e}")

    """获取最终的执行人信息"""
    def _get_execute_user(self):
        if self.env_value.startswith('PathConfig.'):
            config_user = self.env_value.split('.')[1]
        else:
            config_user = self.env_value
        print(f"配置文件中的执行人: {config_user}")
        print(f"Jenkins传入的执行人: {self.bulid_user_name}")
        return self.bulid_user_name or config_user

    """插入测试报告表并返回报告ID"""
    def _insert_test_report(self, db_helper, execute_user, test_plan_name, start_time, update_at):
        try:
            result = db_helper.execute_insert(INSERT_TEST_REPORT,(execute_user,start_time,update_at,test_plan_name))
            print(f'result: {result}')
            if result is not None and result > 0:
                print("测试报告表初始化成功。")
                return self._get_latest_report_id(db_helper, execute_user)
            else:
                print("测试报告表初始化失败。")
        except Exception as e:
            print(f"测试报告表初始化时发生错误: {e}")
        return None

    """查询最新的测试报告ID"""
    def _get_latest_report_id(self, db_helper, execute_user):
        try:
            result = db_helper.find_one(SELECT_LATEST_REPORT_ID,execute_user)
            if result:
                report_id = result['id']
                print(f"查询到的测试报告ID: {report_id}")
                return report_id
            else:
                print("未查询到测试报告ID。")
        except Exception as e:
            print(f"查询测试报告ID时发生错误: {e}")
        return None

    """初始化测试用例执行结果表"""
    def _initialize_test_cases(self, db_helper, report_id):
        for case_index, case_data in enumerate(self.final_case_list):
            case_data['testreportid'] = report_id
            project, business, level, test_id = self._extract_case_info(case_data)
            test_scene, write_user = self._extract_case_scene(case_data)
            case_path = case_data['report_part_path'].replace('\\', '/')
            print(f'project:{project}, business:{business},level:{level},test_id:{test_id},test_scene:{test_scene},write_user:{write_user}')
            '''
            sql = f"""
            INSERT INTO tep_minipro_web.mini_test_report_case(
                testreportid, testcaseid, project, business, level, testid, test_scene, case_path,
                start_time, end_time, self.execute_time, status, report_url, update_at, write_user
            ) VALUES (
                {report_id}, NULL, '{project}', '{business}', {level}, '{test_id}', '{test_scene or ''}',
                '{case_path}', NULL, NULL, NULL, 0, NULL, '{self.start_time}', '{write_user or ''}'
            )
            """
            '''

            print(f"初始化测试用例SQL语句: {INSERT_TEST_REPORT_CASE}")
            try:
                result = db_helper.execute_insert(INSERT_TEST_REPORT_CASE,(report_id,project,business,level,test_id,test_scene or '',case_path,self.start_time,write_user or ''))
                if result is not None and result > 0:
                    print(f"测试用例初始化成功: {INSERT_TEST_REPORT_CASE}")
                else:
                    print(f"测试用例初始化失败: {INSERT_TEST_REPORT_CASE}")
            except Exception as e:
                print(f"测试用例初始化时发生错误: {e}")

    """提取测试用例的基本信息"""
    def _extract_case_info(self, case_data):

        # pre_project = (case_data['case_path'].replace(BASEDIR, '')).split("\\")[1]
        # project = CASEDIR_MAPPING.get(pre_project, pre_project)
        # print(project)

        # pre_business = (case_data['case_path'].replace(BASEDIR, '')).split("\\")[2]
        # business = CASEDIR_MAPPING.get(pre_business, pre_business)
        # print(business)

        # pre_level = (case_data['case_path'].replace(BASEDIR, '')).split("\\")[3].replace('P', '')
        # level = int(pre_level)
        # print(level)
        
        relative_path = os.path.relpath(case_data['case_path'], BASEDIR)
        parts = relative_path.split(os.sep)
        
        pre_project = parts[0] 
        project = CASEDIR_MAPPING.get(pre_project, pre_project)
        
        pre_business = parts[1] 
        business = CASEDIR_MAPPING.get(pre_business, pre_business)

        pre_level = parts[2].replace('P', '')
        level = int(pre_level)

        test_id = case_data['file_name']
        return project, business, level, test_id

    """从用例文件中提取测试场景和编写人"""
    def _extract_case_scene(self, case_data):
        test_id = case_data['file_name']
        script_path = os.path.join(case_data['case_path'], f"{test_id}.py")
        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                content = file.read()
            test_scene = re.search(r'__desc__\s*=\s*["\'](.*?)["\']', content).group(1) if re.search(
                r'__desc__\s*=\s*["\'](.*?)["\']', content) else None
            write_user = re.search(r'__author__\s*=\s*["\'](.*?)["\']', content).group(1) if re.search(
                r'__author__\s*=\s*["\'](.*?)["\']', content) else None
            return test_scene, write_user
        except FileNotFoundError:
            print(f"文件未找到: {script_path}")
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
        return None, None




