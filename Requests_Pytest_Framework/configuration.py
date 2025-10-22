import json
import os.path
import pytest
from datetime import datetime



@pytest.hookimpl(tryfirst=True)
def pytest_config(config):
    report_dir = 'reports'
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    config.option.htmlpath = f"{report_dir}/report_{now}.html"


@pytest.fixture(scope='session',autouse=True)
def setup_teaddown():
    print('\nSetting up resources...')
    yield
    print('\nTearing down resources...')


@pytest.fixture
def load_user_data():
    file_path = os.path.join(os.path.dirname(__file__),'data','test_data.json')
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data