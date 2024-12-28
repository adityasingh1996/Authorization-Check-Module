# keygen.py
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime
import base64

def generate_weekly_key():
    with open('private_key.pem', 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    
    week = datetime.now().isocalendar()[1]
    year = datetime.now().year
    message = f"{year}:{week}".encode()
    
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

if __name__ == "__main__":
    print(f"This week's key: {generate_weekly_key()}")