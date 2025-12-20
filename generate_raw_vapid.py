from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

def generate_keys():
    # Generate EC key pair (P-256 curve)
    key = ec.generate_private_key(ec.SECP256R1(), default_backend())

    # Get public key in uncompressed point format (X9.62), then base64url encode
    pub_raw = key.public_key().public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint
    )
    public_key = base64.urlsafe_b64encode(pub_raw).decode().rstrip('=')

    # Get private key as raw bytes (the 'd' value)
    private_numbers = key.private_numbers()
    d_bytes = private_numbers.private_value.to_bytes(32, byteorder='big')
    private_key = base64.urlsafe_b64encode(d_bytes).decode().rstrip('=')

    print('='*60)
    print('NEW VAPID KEYS (Raw Base64URL format for pywebpush)')
    print('='*60)
    print()
    print('VAPID_PRIVATE_KEY=' + private_key)
    print()
    print('VAPID_PUBLIC_KEY=' + public_key)
    print()
    print('='*60)
    print('Instructions:')
    print('1. Add these variables to your Railway .env / environment variables.')
    print('2. Restart the deployment.')
    print('3. Re-enable notifications in the app (old subscriptions will fail).')
    print('='*60)

if __name__ == "__main__":
    generate_keys()
