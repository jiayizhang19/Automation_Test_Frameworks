from concurrent.futures import ThreadPoolExecutor

def check_login_status():
    ...

def check_activate_account():
    ...

def check_privacy_policy():
    ...

def check_company_selection():
    ...

def before_login_bfd():
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(check_login_status),
            executor.submit(check_activate_account),
            executor.submit(check_privacy_policy),
            executor.submit(check_company_selection)
        ]
    for future in futures:
        future.result()