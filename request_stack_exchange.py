import requests
import json

response = requests.get("https://api.stackexchange.com/2.2/questions?order=desc&sort=activity&site=stackoverflow")

print(response)
print(response.status_code)
print(response.headers)
print(response.json())

