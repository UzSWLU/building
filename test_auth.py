#!/usr/bin/env python3
"""
Auth integratsiyasini test qilish uchun script
"""

import requests
import json

# Test sozlamalari
BASE_URL = "http://localhost:8001/api"
TEST_TOKEN = "your_test_token_here"  # Bu yerga haqiqiy token qo'ying

def test_health_check():
    """Health check test"""
    print("🔍 Health check test...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check xatolik: {e}")
        return False

def test_without_token():
    """Token siz so'rov test"""
    print("\n🔍 Token siz so'rov test...")
    try:
        response = requests.get(f"{BASE_URL}/buildings/")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ 401 xatolik to'g'ri - token talab qilinadi")
            return True
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

def test_with_invalid_token():
    """Noto'g'ri token bilan test"""
    print("\n🔍 Noto'g'ri token test...")
    try:
        headers = {"Authorization": "Bearer invalid_token_123"}
        response = requests.get(f"{BASE_URL}/buildings/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ 401 xatolik to'g'ri - noto'g'ri token")
            return True
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

def test_with_valid_token():
    """To'g'ri token bilan test"""
    print("\n🔍 To'g'ri token test...")
    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.get(f"{BASE_URL}/buildings/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ 200 muvaffaqiyat - token to'g'ri")
            return True
        elif response.status_code == 401:
            print("❌ 401 xatolik - token noto'g'ri yoki muddati o'tgan")
            return False
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

def test_query_parameter_token():
    """Query parameter orqali token test"""
    print("\n🔍 Query parameter token test...")
    try:
        response = requests.get(f"{BASE_URL}/buildings/?access_token={TEST_TOKEN}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ 200 muvaffaqiyat - query parameter token ishlaydi")
            return True
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

def test_post_with_token():
    """POST so'rov bilan token test"""
    print("\n🔍 POST so'rov test...")
    try:
        headers = {
            "Authorization": f"Bearer {TEST_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "name": "Test bino",
            "description": "Test uchun yaratilgan bino"
        }
        response = requests.post(f"{BASE_URL}/buildings/", headers=headers, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ POST muvaffaqiyat - yozish ruxsati bor")
            return True
        elif response.status_code == 403:
            print("❌ 403 xatolik - yozish ruxsati yo'q (user role)")
            return False
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

def main():
    """Asosiy test funksiyasi"""
    print("🚀 Auth integratsiyasini test qilish boshlandi...")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Token: {TEST_TOKEN[:10]}..." if len(TEST_TOKEN) > 10 else f"Test Token: {TEST_TOKEN}")
    
    tests = [
        test_health_check,
        test_without_token,
        test_with_invalid_token,
        test_with_valid_token,
        test_query_parameter_token,
        test_post_with_token,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 50)
    
    print(f"\n📊 Test natijalari: {passed}/{total} muvaffaqiyatli")
    
    if passed == total:
        print("🎉 Barcha testlar muvaffaqiyatli!")
    else:
        print("⚠️  Ba'zi testlar muvaffaqiyatsiz. Loglarni tekshiring.")

if __name__ == "__main__":
    main()
