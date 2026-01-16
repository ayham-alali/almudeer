import requests
import os
import secrets
import json

# Configuration
BASE_URL = "https://almudeer.up.railway.app"
ADMIN_KEY = os.getenv("ADMIN_KEY", "Jo7hd1Qzocj2v2R55NTajqPzybvbuxDEQXv5osZx5kE")

def print_result(name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_backend():
    print(f"=== Verifying Backend Improvements ({BASE_URL}) ===\n")
    
    headers = {"X-Admin-Key": ADMIN_KEY}
    
    # 1. Test Set/Get Signing Fingerprint
    print("\n--- Testing Signing Fingerprint ---")
    
    # First, get current fingerprint to restore later
    current_fingerprint = ""
    try:
        resp = requests.get(f"{BASE_URL}/api/app/version-check")
        if resp.status_code == 200:
            current_fingerprint = resp.json().get("apk_signing_fingerprint") or ""
            print(f"ℹ️ Original Fingerprint: {current_fingerprint}")
    except:
        pass

    # Set fingerprint
    test_fingerprint = "A" * 64
    try:
        resp = requests.post(
            f"{BASE_URL}/api/app/set-signing-fingerprint",
            headers=headers,
            params={"fingerprint": test_fingerprint}
        )
        if resp.status_code == 200:
            print_result("Set Fingerprint", True, resp.json().get("message"))
        else:
            print_result("Set Fingerprint", False, f"Status: {resp.status_code}, {resp.text}")
    except Exception as e:
        print_result("Set Fingerprint", False, str(e))

    # Check version endpoint
    try:
        resp = requests.get(f"{BASE_URL}/api/app/version-check")
        if resp.status_code == 200:
            data = resp.json()
            fp = data.get("apk_signing_fingerprint")
            success = fp == test_fingerprint
            print_result("Verify Fingerprint in /version-check", success, f"Got: {fp}")
        else:
            print_result("Verify Fingerprint in /version-check", False, f"Status: {resp.status_code}")
    except Exception as e:
        print_result("Verify Fingerprint in /version-check", False, str(e))
        
    # Restore original fingerprint
    try:
        print("Restoring original fingerprint...")
        requests.post(
            f"{BASE_URL}/api/app/set-signing-fingerprint",
            headers=headers,
            params={"fingerprint": current_fingerprint}
        )
    except:
        print("Warning: Failed to restore fingerprint")


    # 2. Test Analytics Endpoints
    print("\n--- Testing Analytics Endpoints ---")
    
    endpoints = [
        "/api/app/version-distribution",
        "/api/app/update-funnel",
        "/api/app/time-to-update",
        "/api/app/update-analytics"
    ]
    
    for ep in endpoints:
        try:
            resp = requests.get(f"{BASE_URL}{ep}", headers=headers)
            if resp.status_code == 200:
                print_result(f"GET {ep}", True, "Response OK")
                # print(json.dumps(resp.json(), indent=2))
            else:
                print_result(f"GET {ep}", False, f"Status: {resp.status_code}")
        except Exception as e:
            print_result(f"GET {ep}", False, str(e))

if __name__ == "__main__":
    test_backend()
