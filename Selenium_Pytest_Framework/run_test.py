import subprocess
import os
import sys
import argparse
import json


'''
1. Use argparse(Approach 2 in the below) to handle command-line arguments 
2. provide several functions to recognize and automatically dispatch files according to their types.

'''

# Important! Set the project root directory so that the below command could be run successfully wherever you execute it!
project_root = os.path.dirname(os.path.abspath(__file__))


def run_test(targets=None, markers=None, keyword=None):
    # command = ["pytest"]
    # Use the below command for CI/CD triggering, otherwise current file won't be triggered successfully.
    command = [sys.executable, "-m", "pytest"] 

    if targets:
        if isinstance(targets,list):
            command.extend(targets)
        else:
            command.append(targets)

    if markers:
        command.extend(["-m", markers])
    if keyword:
        command.extend(["-k", keyword]) 

    subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
    )

# Dispatch case with different parameters provided in command lines.
def auto_dispatch_test_files(include_case_path=None, include_case=None, exclude_case=None, exclude_case_path=None, case_level=None):
    pytest_files = []
    airtest_files = []
    seen_files = set()
    
    if include_case_path is None:
        include_case_path = [
            'cases_bfd_regression/',
            'cases_bgdzq_regression/',
            'cases_exchange_regression/',
            'cases_gw_regression/',
            'cases_main_core/',
            'cases_zx_regression/'
        ]
    if case_level is None:
        case_level = ['P0','P1','P2']

    if isinstance(include_case_path, str):
        include_case_path = [include_case_path]
    if include_case_path:
        for path in include_case_path:
            abs_path = os.path.abspath(os.path.join(project_root, path))
            if os.path.isfile(abs_path):
                separate_pytest_airtest_file(abs_path,pytest_files,airtest_files,seen_files,
                                            include_case, exclude_case, exclude_case_path, case_level)
            elif os.path.isdir(abs_path):
                for root, _, files in os.walk(abs_path):
                    if not root.startswith(abs_path):
                        continue
                    for file in files:
                        if file.endswith(".py"):
                            full_path = os.path.join(root, file)
                            separate_pytest_airtest_file(full_path,pytest_files,airtest_files,seen_files, 
                                                     include_case, exclude_case, exclude_case_path, case_level)
    if include_case:
        for root, _, files in os.walk(project_root):
            for file in files:
                if not file.endswith(".py"):
                    continue
                base_name = os.path.splitext(file)[0]
                if base_name in include_case:
                    full_path = os.path.join(root, file)
                    separate_pytest_airtest_file(full_path, pytest_files, airtest_files, seen_files, 
                                                 include_case, exclude_case, exclude_case_path, case_level)
    
    return pytest_files, airtest_files

def separate_pytest_airtest_file(
            full_path, pytest_files, airtest_files, seen_files,
            include_case=None, exclude_case=None, exclude_case_path=None, case_level=None
        ):
    if not full_path.endswith(".py") or full_path in seen_files:
        return
    base_name = os.path.splitext(os.path.basename(full_path))[0]
    level = os.path.basename(os.path.dirname(os.path.dirname(full_path)))
    if level not in case_level:
        return
    if exclude_case and base_name in exclude_case:
        return
    if exclude_case_path:
        for path in exclude_case_path:
            if path in full_path.replace("\\","/"):
                if not include_case or base_name not in include_case:
                    return
    seen_files.add(full_path)
    if is_pytest_file(full_path):
        pytest_files.append(full_path)
    else:
        base_name = os.path.basename(full_path).replace(".py","")
        airtest_files.append(base_name)

def is_pytest_file(file_path):
    file_path = os.path.join(project_root,file_path)
    try:
        with open(file_path,"r",encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.strip().startswith("def test_") or line.strip().startswith("@pytest."):
                    return True
        return False
    except FileNotFoundError as e:
        print(f"'{file_path}': {e}")
        return False
    except PermissionError as e:
        print(f"'{file_path}': {e}")
        return False



if __name__ == "__main__":
    ''' Approach 1: Exectute the current file directly '''
    # run_test(
        # targets=[
        #     "cases_bfd_regression/testcases_movie/P0/movie-9.air",
        #     "cases_bfd_regression/testcases_movie/P0/movie-10.air"
        # ],
        # markers="bfd_movie",
        # keyword="",
    # )

    ''' Approach 2: Execute the current file with command-line arguments '''
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--targets', type=str, nargs='+', default=["cases_bfd_regression/testcases_movie/P0/movie-9.air"])
    # args = parser.parse_args()
    # targets_from_env = os.environ.get("TARGETS")
    # if not args.targets and targets_from_env:
    #     args.targets = targets_from_env.split()
    # pytest_run(targets=args.targets)

    ''' Approach 3: Execute the current file with command-line arguments for different inputs'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--case_path', type=str, nargs='+', default=["TestCases"])
    parser.add_argument('--exclude_cases_dirs', type=str, nargs='+', default=[])
    parser.add_argument('--include_cases', type=str, nargs='+', default=[])
    parser.add_argument('--exclude_cases', type=str, nargs='+', default=[])

    args = parser.parse_args()
    pytest_case, airtest_case = auto_dispatch_test_files(
        case_path=args.case_path, 
        include_case=args.include_cases, 
        exclude_case=args.exclude_cases,
        exclude_case_path=args.exclude_cases_dirs
        )
        
    if airtest_case:
        # 运行测试
        print(f"airtest run {airtest_case}")
        # x = Run(
                # case_path=airtest_case, 
                # include_cases=airtest_case,
                # include_cases=args.include_cases, 
                # exclude_cases=args.exclude_cases,
                # )
        # x.run()

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
        run_test(
            targets=pytest_case
        )

        


