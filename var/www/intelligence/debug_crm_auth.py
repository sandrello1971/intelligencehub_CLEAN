#!/usr/bin/env python3

import requests
import os
import json

CRM_API_KEY = os.getenv("CRM_API_KEY")
CRM_USERNAME = os.getenv("CRM_USERNAME") 
CRM_PASSWORD = os.getenv("CRM_PASSWORD")
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://api.crmincloud.it")

print(f"🔧 Debug CRM Auth...")
print(f"API Key: {CRM_API_KEY[:20]}...")
print(f"Username: {CRM_USERNAME}")
print(f"Base URL: {CRM_BASE_URL}")

url = f"{CRM_BASE_URL}/api/v1/Auth/Login"
payload = {
    "grant_type": "password",
    "username": CRM_USERNAME,
    "password": CRM_PASSWORD
}
headers = {
    "WebApiKey": CRM_API_KEY,
    "Content-Type": "application/json"
}

print(f"🌐 URL: {url}")
print(f"📦 Payload: {payload}")
print(f"📋 Headers: {headers}")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Token: {token[:50]}...")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"💥 Exception: {e}")
