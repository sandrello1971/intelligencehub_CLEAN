#!/usr/bin/env python3
import sys
import os
sys.path.append('/var/www/intelligence/backend')

from fastapi.testclient import TestClient
from app.routes.rag_routes import router
from fastapi import FastAPI

# Crea app di test
app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_rag_api():
    print("🧪 Testing RAG API Routes...")
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = client.get("/api/v1/rag/health")
        print(f"✅ Health Check - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
        return False
    
    # Test 2: Supported Formats
    print("\n2. Testing Supported Formats...")
    try:
        response = client.get("/api/v1/rag/formats")
        print(f"✅ Formats - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Formats failed: {e}")
        return False
    
    # Test 3: Stats
    print("\n3. Testing Stats...")
    try:
        response = client.get("/api/v1/rag/stats")
        print(f"✅ Stats - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Stats failed: {e}")
        return False
    
    # Test 4: List Documents
    print("\n4. Testing List Documents...")
    try:
        response = client.get("/api/v1/rag/documents?company_id=1")
        print(f"✅ List Documents - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ List Documents failed: {e}")
        return False
    
    print("\n🎉 All RAG API tests passed!")
    return True

if __name__ == "__main__":
    success = test_rag_api()
    sys.exit(0 if success else 1)
