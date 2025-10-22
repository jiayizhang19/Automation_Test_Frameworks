import requests

url = "http://20.0.147.210:5000/gemini"
headers = {
    "Content-Type": "application/json"
}
data = {
    "prompt": "tell me about the future of ai"
}

response = requests.post(url, headers=headers, json=data)

try:
    response.raise_for_status()  # Check if the request was successful
    print(response.json())
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except requests.exceptions.RequestException as req_err:
    print(f"Request error occurred: {req_err}")
except requests.exceptions.JSONDecodeError:
    print("Response is not in JSON format:")
    print(response.text)