import requests
import json

# تست API login
def test_login(username, password):
    url = "http://127.0.0.1:8000/api/auth/login/"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Testing login for: {username}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful!")
            print(f"Access Token: {result.get('access', 'Not found')[:50]}...")
            print(f"User ID: {result.get('user', {}).get('id', 'Not found')}")
            print(f"Username: {result.get('user', {}).get('username', 'Not found')}")
            return True
        else:
            print("❌ Login failed!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# تست کاربران مختلف
print("=== Testing Login API ===\n")

# تست superuser ها
print("1. Testing admin user:")
test_login("admin", "admin123")

print("\n2. Testing pardach user:")  
test_login("pardach", "رمز عبوری که وارد کردید")

print("\n3. Testing simple user:")
test_login("test", "test123") 