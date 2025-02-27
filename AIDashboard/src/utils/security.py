# utils/security.py
from cryptography.fernet import Fernet
from models.user import User

key = Fernet.generate_key()  # Store securely
cipher = Fernet(key)

def encrypt_api_key(api_key: str) -> str:
    return cipher.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    return cipher.decrypt(encrypted_key.encode()).decode()

# Example usage
user.exchanges.append(ExchangeConfig(
    exchange_name="binance",
    api_key=encrypt_api_key("my_api_key"),
    api_secret=encrypt_api_key("my_secret")
))