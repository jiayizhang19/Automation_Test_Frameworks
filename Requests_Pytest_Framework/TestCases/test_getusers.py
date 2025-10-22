import uuid
import pytest
from configuration import *
from utils.apis import Apis

@pytest.fixture(scope='module')
def api():
    return Apis()

def test_get_users(api):
    response = api.get_request('/users')
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_users(api,load_user_data):
    # payload = {
    #     'name': 'Jerry',
    #     'username': 'Jiayi',
    #     'email': 'test@gmail.com'
    # }
    payload = load_user_data['new_user']
    unique_email = f'{uuid.uuid4().hex[:8]}@gmail.com'
    payload['email'] = unique_email
    response = api.post_request('/users', payload)
    print(response.json())
    assert response.status_code == 201
    assert len(response.json()) > 0
    assert response.json()['name'] == payload['name']

def test_update_users(api):
    payload = {
        'name': 'Jerry',
        'username': 'Jiayi',
        'email': 'test@gmail.com'
    }
    response = api.put_request('/users/1', payload)
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_delete_users(api):
    response = api.delete_request('/users/1')
    print(response.json())
    assert response.status_code == 200
