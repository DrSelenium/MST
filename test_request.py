import requests
import json

url = 'http://127.0.0.1:5000/mst-calculation'

# Load the test data
with open('test.json', 'r') as f:
    data = json.load(f)

headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=data, headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())
except Exception as e:
    print('Error:', e)
