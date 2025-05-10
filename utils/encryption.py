import os
import dotenv
from cryptography.fernet import Fernet
import base64

# Load environment variables
dotenv.load_dotenv()

# Fetch the Fernet key from the environment variable and decode it
raw_key = os.getenv("FERNET_KEY").encode()  # The key should already be base64 encoded
key = Fernet(raw_key)

def encrypt(piece_of_data):
    try:
        if isinstance(piece_of_data, str):
            piece_of_data = piece_of_data.encode('utf-8') 
        elif isinstance(piece_of_data, int):
            piece_of_data = str(piece_of_data).encode('utf-8')
        elif not isinstance(piece_of_data, bytes):
            raise Exception("Invalid data type given.")
        
        encrypted_data = key.encrypt(piece_of_data)
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8') 

    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt(piece_of_data:str):
    try:
        # Decode the base64-encoded string into bytes
        decoded_data = base64.urlsafe_b64decode(piece_of_data)
        decrypted_data = key.decrypt(decoded_data)

        return decrypted_data.decode('utf-8')  # Return the decrypted data as a string
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
