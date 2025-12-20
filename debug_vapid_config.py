
import os
import sys
import base64
import json
from services.push_service import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_CLAIMS_EMAIL

def check_keys():
    print("="*60)
    print("VAPID CONFIGURATION DIAGNOSTIC")
    print("="*60)
    
    # 1. Check Public Key
    print(f"[*] Checking Public Key...")
    if not VAPID_PUBLIC_KEY:
        print("❌ ERROR: VAPID_PUBLIC_KEY is not set or empty")
    else:
        print(f"✅ FOUND. Length: {len(VAPID_PUBLIC_KEY)}")
        print(f"   Value (first 10 chars): {VAPID_PUBLIC_KEY[:10]}...")
        try:
            # Check if valid base64url
            decoded = base64.urlsafe_b64decode(VAPID_PUBLIC_KEY + "==")
            if len(decoded) == 65:
                print("✅ FORMAT: Valid Uncompressed Point (65 bytes)")
            else:
                print(f"⚠️ WARNING: Unexpected length {len(decoded)} bytes (expected 65)")
        except Exception as e:
            print(f"❌ ERROR: Invalid Base64URL: {e}")

    print("-" * 30)

    # 2. Check Private Key
    print(f"[*] Checking Private Key...")
    if not VAPID_PRIVATE_KEY:
        print("❌ ERROR: VAPID_PRIVATE_KEY is not set or empty")
    else:
        print(f"✅ FOUND. Length: {len(VAPID_PRIVATE_KEY)}")
        # Don't print full key for security, just check format
        if VAPID_PRIVATE_KEY.startswith("-----BEGIN"):
            print("⚠️ WARNING: Key looks like PEM format. push_service should have converted this!")
        else:
            try:
                decoded = base64.urlsafe_b64decode(VAPID_PRIVATE_KEY + "==")
                if len(decoded) == 32:
                    print("✅ FORMAT: Valid Raw Private Key (32 bytes)")
                else:
                    print(f"⚠️ WARNING: Unexpected length {len(decoded)} bytes (expected 32)")
            except Exception as e:
                print(f"❌ ERROR: Invalid Base64URL: {e}")

    print("-" * 30)
    
    # 3. Check Email
    print(f"[*] Checking Claims Email...")
    print(f"   Value: {VAPID_CLAIMS_EMAIL}")
    if VAPID_CLAIMS_EMAIL.startswith("mailto:") or VAPID_CLAIMS_EMAIL.startswith("https:"):
        print("✅ FORMAT: Valid")
    else:
        print("❌ ERROR: Must start with 'mailto:' or 'https:'")

    print("="*60)
    
    # 4. Check Environment Raw Values (Debug only)
    raw_priv = os.getenv("VAPID_PRIVATE_KEY")
    if raw_priv:
        print(f"DEBUG: Raw Env Private Key Starts with: {raw_priv[:15]}...")
    else:
        print("DEBUG: Raw Env Private Key is None")

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    check_keys()
