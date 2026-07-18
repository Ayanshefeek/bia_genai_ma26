import requests

url = "http://127.0.0.1:8000/webhooks/support"

payload = {
    "student_name": "Srimanth",
    "issue": "I am facing issues with my assignment"
}

response = requests.post(
    url,
    json = payload
)

print(response.json())