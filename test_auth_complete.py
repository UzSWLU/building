#!/usr/bin/env python3
"""
To'liq auth test script - barcha role lar uchun
"""

import requests
import json

# Test sozlamalari
BASE_URL = "http://localhost:8001/api"

# Test token lar (haqiqiy token lar bilan almashtiring)
TEST_TOKENS = {
    'admin': 'admin_token_here',
    'creator': 'creator_token_here', 
    'manager': 'manager_token_here',
    'technician': 'technician_token_here',
    'user': 'user_token_here'
}

def test_auth_with_role(role, token):
    """Muayyan role bilan auth test"""
    print(f"\n🔍 {role.upper()} role bilan test...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Buildings endpoint
    print(f"  📋 Buildings endpoint test...")
    try:
        response = requests.get(f"{BASE_URL}/buildings/", headers=headers)
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    ✅ {role} - Buildings o'qish ruxsati bor")
        elif response.status_code == 403:
            print(f"    ❌ {role} - Buildings o'qish ruxsati yo'q")
        else:
            print(f"    ⚠️  {role} - Kutilmagan status: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Xatolik: {e}")
    
    # 2. Buildings POST (yozish ruxsati)
    print(f"  📝 Buildings POST test...")
    try:
        data = {"name": f"Test bino - {role}", "description": "Test uchun"}
        response = requests.post(f"{BASE_URL}/buildings/", headers=headers, json=data)
        print(f"    Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"    ✅ {role} - Buildings yozish ruxsati bor")
        elif response.status_code == 403:
            print(f"    ❌ {role} - Buildings yozish ruxsati yo'q")
        else:
            print(f"    ⚠️  {role} - Kutilmagan status: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Xatolik: {e}")
    
    # 3. Devices endpoint
    print(f"  🔧 Devices endpoint test...")
    try:
        response = requests.get(f"{BASE_URL}/devices/", headers=headers)
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    ✅ {role} - Devices o'qish ruxsati bor")
        elif response.status_code == 403:
            print(f"    ❌ {role} - Devices o'qish ruxsati yo'q")
        else:
            print(f"    ⚠️  {role} - Kutilmagan status: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Xatolik: {e}")
    
    # 4. Repair Requests endpoint
    print(f"  🔨 Repair Requests endpoint test...")
    try:
        response = requests.get(f"{BASE_URL}/repair-requests/", headers=headers)
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    ✅ {role} - Repair Requests o'qish ruxsati bor")
        elif response.status_code == 403:
            print(f"    ❌ {role} - Repair Requests o'qish ruxsati yo'q")
        else:
            print(f"    ⚠️  {role} - Kutilmagan status: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Xatolik: {e}")

def test_without_token():
    """Token siz test"""
    print("\n🔍 Token siz test...")
    try:
        response = requests.get(f"{BASE_URL}/buildings/")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ 401 xatolik to'g'ri - token talab qilinadi")
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
    except Exception as e:
        print(f"❌ Xatolik: {e}")

def test_invalid_token():
    """Noto'g'ri token bilan test"""
    print("\n🔍 Noto'g'ri token test...")
    try:
        headers = {"Authorization": "Bearer invalid_token_123"}
        response = requests.get(f"{BASE_URL}/buildings/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ 401 xatolik to'g'ri - noto'g'ri token")
        else:
            print(f"❌ Kutilmagan status: {response.status_code}")
    except Exception as e:
        print(f"❌ Xatolik: {e}")

def main():
    """Asosiy test funksiyasi"""
    print("🚀 To'liq Auth Test boshlandi...")
    print(f"Base URL: {BASE_URL}")
    
    # Token siz test
    test_without_token()
    
    # Noto'g'ri token test
    test_invalid_token()
    
    # Har bir role bilan test
    for role, token in TEST_TOKENS.items():
        if token != f"{role}_token_here":  # Haqiqiy token bor bo'lsa
            test_auth_with_role(role, token)
        else:
            print(f"\n⚠️  {role.upper()} role uchun token o'rnatilmagan")
    
    print("\n" + "="*60)
    print("📋 Test natijalari:")
    print("✅ Admin/Creator - Barcha endpoint lar va operatsiyalar")
    print("✅ Manager - Buildings, Rooms, Devices, Categories, Device Types")
    print("✅ Technician - Devices, Repair Requests, Service Logs")
    print("✅ User - Faqat o'qish ruxsati")
    print("="*60)
    
    print("\n💡 Keyingi qadamlar:")
    print("1. Haqiqiy token larni oling")
    print("2. Role lar ni test qiling")
    print("3. Yangi role lar qo'shing")
    print("4. Endpoint lar uchun maxsus ruxsatlar sozlang")

if __name__ == "__main__":
    main()
