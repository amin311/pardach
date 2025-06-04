import requests

url = "http://127.0.0.1:8000/api/auth/login/"
data = {
    "username": "pardach",
    "password": "pardach123"
}

response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print("✅ Login successful for pardach!")
    print(f"User ID: {result.get('user', {}).get('id', 'Not found')}")
    print(f"Username: {result.get('user', {}).get('username', 'Not found')}")
else:
    print("❌ Login failed!")
    print(f"Response: {response.text}") 