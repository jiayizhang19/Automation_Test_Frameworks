import requests

class Apis:

    base_url = 'https://jsonplaceholder.typicode.com'

    def __init__(self):
        self.header = {
            'content-type': 'application/json'
        }

    def get_request(self, endpoint):
        response = requests.get(
            self.base_url + endpoint,
            headers=self.header
        )
        return response

    def post_request(self, endpoint, payload):
        response = requests.post(
            self.base_url + endpoint,
            headers=self.header,
            json=payload
        )
        return response

    def put_request(self, endpoint, payload):
        response = requests.put(
            self.base_url + endpoint,
            headers=self.header,
            json=payload
        )
        return response

    def delete_request(self, endpoint):
        response = requests.delete(
            self.base_url + endpoint,
            headers=self.header
        )
        return response