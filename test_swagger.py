#!/usr/bin/env python3
"""
Swagger UI ni test qilish uchun script
"""

import requests
import json

def test_swagger_endpoints():
    """Swagger endpoint larni test qilish"""
    base_url = "http://localhost:8001"
    
    print("🔍 Swagger endpoint larni test qilish...")
    
    # 1. Health check
    print("\n1. Health check test...")
    try:
        response = requests.get(f"{base_url}/health/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check ishlaydi")
        else:
            print("❌ Health check ishlamaydi")
    except Exception as e:
        print(f"❌ Health check xatolik: {e}")
    
    # 2. Schema endpoint
    print("\n2. Schema endpoint test...")
    try:
        response = requests.get(f"{base_url}/api/schema/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Schema endpoint ishlaydi")
            schema = response.json()
            print(f"API title: {schema.get('info', {}).get('title', 'N/A')}")
            print(f"API version: {schema.get('info', {}).get('version', 'N/A')}")
        else:
            print("❌ Schema endpoint ishlamaydi")
    except Exception as e:
        print(f"❌ Schema endpoint xatolik: {e}")
    
    # 3. Swagger UI
    print("\n3. Swagger UI test...")
    try:
        response = requests.get(f"{base_url}/api/schema/swagger-ui/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Swagger UI ishlaydi")
            print(f"URL: {base_url}/api/schema/swagger-ui/")
        else:
            print("❌ Swagger UI ishlamaydi")
    except Exception as e:
        print(f"❌ Swagger UI xatolik: {e}")
    
    # 4. ReDoc
    print("\n4. ReDoc test...")
    try:
        response = requests.get(f"{base_url}/api/schema/redoc/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ ReDoc ishlaydi")
            print(f"URL: {base_url}/api/schema/redoc/")
        else:
            print("❌ ReDoc ishlamaydi")
    except Exception as e:
        print(f"❌ ReDoc xatolik: {e}")
    
    # 5. API endpoints test (auth talab qiladi)
    print("\n5. API endpoints test (auth talab qiladi)...")
    try:
        response = requests.get(f"{base_url}/api/buildings/")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Auth middleware ishlaydi - 401 xatolik to'g'ri")
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
    except Exception as e:
        print(f"❌ API endpoint xatolik: {e}")

def main():
    """Asosiy test funksiyasi"""
    print("🚀 Swagger va API test qilish boshlandi...")
    print("Base URL: http://localhost:8001")
    
    test_swagger_endpoints()
    
    print("\n" + "="*60)
    print("📋 Swagger UI manzillari:")
    print("🔗 Swagger UI: http://localhost:8001/api/schema/swagger-ui/")
    print("🔗 ReDoc: http://localhost:8001/api/schema/redoc/")
    print("🔗 Schema JSON: http://localhost:8001/api/schema/")
    print("🔗 Health Check: http://localhost:8001/health/")
    print("="*60)
    
    print("\n💡 Frontend dasturchi uchun:")
    print("1. Swagger UI da barcha endpoint larni ko'rish mumkin")
    print("2. Har bir endpoint da 'Try it out' tugmasi bor")
    print("3. Authorization header qo'shish uchun 'Authorize' tugmasini bosing")
    print("4. Access token ni 'Bearer YOUR_TOKEN' formatida kiriting")

if __name__ == "__main__":
    main()
