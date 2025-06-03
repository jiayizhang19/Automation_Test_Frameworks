"""
Note: Following configurations will be applied to overall test cases under this project.

Now we are having three conftest.py in different folders, to be specific:
 - airtest_pytest_framework/conftest.py                                 # outer session fixture
 - airtest_pytest_framework/regression/test_suites_1/conftest.py        # local session fixture
 - airtest_pytest_framework/regression/test_suites_2/conftest.py        # local session fixture


Pytest treats each conftest.py file as a separate fixture source.
Even though they each define a scope="session" fixture, they are scoped only to the tests inside their own subdirectories.
Since the fixture functions are defined in separate modules, they are considered separate fixtures — even if they have the same name.
So:
pytest runs the outer session fixture once globally.
It then runs the local session fixture inside each folder once per folder, for the tests under that folder only.

"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from airtest.core.api import *
from airtest.report.report import LogToHtml
import configparser
from airtest_pytest_framework.conf.config import PathConfig
from airtest_pytest_framework.utils.case_manager.testcase_manager import Manage_cases
from airtest_pytest_framework.utils.report_manager.test_report_manager import ReportManager
from airtest_pytest_framework.utils.message_manager.message_sender import Message_manager

using("common/publicAction_testsuites_1.air")
from publicAction_testsuites_1 import *

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'conf','conf.ini'),encoding='utf-8')
env = eval(config.get('environment','env'))
airtest_report_dir = env.report_path
write_db_flag = config.getboolean('write_db','write_db_flag',fallback=False)


@pytest.fixture(scope="session", autouse=True)
def setup_update_overall_reports():
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H-%M-%S_%f")
    case_info_json = os.environ.get("PYTEST_CASE_INFO")
    if not case_info_json:
        raise ValueError("pytest run: no test")
    case_info = json.loads(case_info_json)
    case_paths = case_info.get("case_paths",[])

    # This is to ensure single message could be sent successfully according to specific case
    base_paths = list({
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(path))))
        for path in case_paths
    })
    full_case_info = [parse_case_info(path, timestamp) for path in case_paths]
    message_info_json = os.environ.get('MESSAGE_INFO')
    message_info = json.loads(message_info_json)

    manage_cases = Manage_cases(
        case_path=base_paths,
        include_cases=case_paths, 
        start_time=start_time,
    )

    report_manager = ReportManager(
        manage_cases,
        final_case_list=full_case_info,  
        start_time=start_time,
    )

    message_manager = Message_manager(
        manage_cases,
        start_time=start_time,
        node_name=message_info.get('node_name'),
        dingding_token=message_info.get('dingding_token'),
        single_send_flag=message_info.get('single_send_flag'),
    )
    

    report_manager.initialize_test_report_and_cases()

    yield {
        "timestamp":str(timestamp),
        "start_time": start_time,
        "manage_cases": manage_cases,
        "report_manager": report_manager,
        "message_manager": message_manager
    }


    report_manager.process_report()


    result = report_manager.get_final_report()


    if write_db_flag and all(
        hasattr(message_manager,attr) for attr in ['testreportid','project_name', 'test_plan_name']
    ):
        message_manager.send_all_result(result)
    else:
        print('testreportid or project_name or test_plan_name was not set.')


@pytest.fixture(scope="module",autouse=True)
def setup_update_single_report(request, setup_update_overall_reports, cleanup_env):
    test_file = request.module.__file__
    case_info = parse_case_info(test_file, setup_update_overall_reports["timestamp"])
    os.makedirs(case_info['report_path'],exist_ok=True)
    auto_setup(
        basedir=os.path.dirname(test_file),
        logdir=case_info['report_path'],
        project_root=os.path.dirname(test_file),
    )
    yield

    h = LogToHtml(
        script_root=os.path.dirname(test_file),
        log_root=case_info['report_path'],
        export_dir=case_info['report_path'],
        lang="zh"
    )
    h.report()

    manage_cases = setup_update_overall_reports["manage_cases"]
    report_manager = setup_update_overall_reports["report_manager"]
    message_manager = setup_update_overall_reports["message_manager"]


    one_report = report_manager.get_one_report(
        case_info["case_path"], 
        case_info["file_name"]
    )

    report_manager.upload_report(one_report)

    report_manager.update_report_data(case_info, one_report)


    # Step 1: pass case_path manually to manage_cases to ensure single message delivery, otherwise it will be a failure
    manage_cases.case_path = case_info["case_path"] 
    # Step 2: send single message of different test cases 
    if write_db_flag:
        message_manager.send_result(
            case_info["file_name"],
            one_report["case_result"],
            one_report["case_name"],
            case_info["report_part_path"]
        )
        for attr in ['testreportid','project_name', 'test_plan_name']:
            setattr(setup_update_overall_reports['message_manager'], attr, getattr(message_manager, attr))



def parse_case_info(path, timestamp):
    test_name = os.path.splitext(os.path.basename(path))[0]
    rel_parts = os.path.relpath(path, start=os.path.join(os.getcwd(), "airtest_pytest_framework"))
    path_parts = rel_parts.split(os.sep)
    if len(path_parts) < 4:
        raise ValueError(f"Invalid test file path: {path}")
    category, business, level = path_parts[1:4]
        
    report_dir = os.path.join(
            airtest_report_dir,
            category,
            business,
            level + "__" + timestamp
        )
    return {
        "case_path": os.path.dirname(path),
        "file_name": test_name,
        "log_path": report_dir,
        "report_path": report_dir,
        "report_part_path": f"{category}/{business}/{level}"
    }







