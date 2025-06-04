#!/usr/bin/env python
"""
اسکریپت تست API endpoints
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_api_endpoint(method, endpoint, data=None, headers=None):
    """تست یک endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        
        print(f"\n📍 {method.upper()} {endpoint}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code < 400:
            print("✅ موفق")
            if response.content:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"📝 تعداد آیتم‌ها: {len(data)}")
                    elif isinstance(data, dict):
                        print(f"📝 کلیدها: {list(data.keys())}")
                except:
                    print("📝 پاسخ غیر JSON")
        else:
            print("❌ خطا")
            try:
                error_data = response.json()
                print(f"📝 خطا: {error_data}")
            except:
                print(f"📝 خطا: {response.text}")
                
    except Exception as e:
        print(f"\n📍 {method.upper()} {endpoint}")
        print(f"💥 خطای ارتباط: {e}")

def test_authentication():
    """تست احراز هویت"""
    print("🔐 تست احراز هویت...")
    
    # تست لاگین
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"\n📍 POST /api/auth/login/")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ لاگین موفق")
        tokens = response.json()
        access_token = tokens.get('access')
        print(f"🎫 Access Token دریافت شد")
        return f"Bearer {access_token}"
    else:
        print("❌ لاگین ناموفق")
        try:
            print(f"📝 خطا: {response.json()}")
        except:
            print(f"📝 خطا: {response.text}")
        return None

def main():
    print("🚀 تست API Endpoints")
    print("=" * 50)
    
    # تست endpoint های عمومی
    public_endpoints = [
        ('GET', '/'),
        ('GET', '/api/docs/'),
        ('GET', '/api/auth/'),
        ('GET', '/api/print-locations/'),
    ]
    
    print("\n🌍 تست Endpoints عمومی:")
    for method, endpoint in public_endpoints:
        test_api_endpoint(method, endpoint)
    
    # تست احراز هویت
    auth_token = test_authentication()
    
    if auth_token:
        # تست endpoint های محافظت شده
        protected_endpoints = [
            ('GET', '/api/core/'),
            ('GET', '/api/dashboard/'),
            ('GET', '/api/business/'),
            ('GET', '/api/designs/'),
            ('GET', '/api/orders/'),
        ]
        
        print("\n🔒 تست Endpoints محافظت شده:")
        headers = {'Authorization': auth_token}
        for method, endpoint in protected_endpoints:
            test_api_endpoint(method, endpoint, headers=headers)
    
    print("\n" + "=" * 50)
    print("✨ تست کامل شد!")

if __name__ == '__main__':
    main() 