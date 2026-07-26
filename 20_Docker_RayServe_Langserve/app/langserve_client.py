import requests

response=requests.post(
    "http://localhost:8000/poem/invoke",
    json={'input':{'topic':"my pet cat"}})

print(response.json()["output"]["content"])