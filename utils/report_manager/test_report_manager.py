
import configparser
conf = configparser.ConfigParser()
conf.read(os.path.join(CONFIGDIR, 'conf.ini'), encoding='utf-8')


class ReportManager:
    def __init__(self,manage_cases:Manage_cases,bulid_user_name=None, test_plan_name=None, test_plan_id=None,final_case_list=None, start_time=None):
        pass
        

    # 基础方法：准备报告目录
    def prepare_dirs(self, dirs_path, save_dirs_num=3):
        pass

    # 基础方法：准备报告目录、日志目录
    def prepare_report_dir(self,report_part_path):
        pass


    def get_final_report(self):
        pass

    def process_report(self):
        pass

    def get_one_report(self, case_path=None, file_name=None):
        pass


    def update_report_task(self):
        pass

    def update_report_data(self,case,one_report):
       pass


    def upload_report(self,one_report):
        pass


    def initialize_test_report_and_cases(self):
        pass


    def _initialize_test_cases(self, db_helper, report_id):
        pass


    def _extract_case_info(self, case_data):
        pass


    def _extract_case_scene(self, case_data):
       pass