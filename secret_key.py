from cryptography.fernet import Fernet

# Tạo một Fernet key
secret_key = Fernet.generate_key()
print(secret_key)