# roulette_game/encryption.py
import json
from cryptography.fernet import Fernet
import os

# --- Key Management ---
KEY_PATH = "roulette_game/secret.key" # Define as a module constant

def generate_key_bytes():
    """Generates a new Fernet key."""
    return Fernet.generate_key()

def save_key(key_bytes, path=KEY_PATH):
    """Saves the key to a file."""
    os.makedirs(os.path.dirname(path), exist_ok=True) # Ensure directory exists
    with open(path, "wb") as key_file:
        key_file.write(key_bytes)

def load_key_bytes(path=KEY_PATH):
    """Loads the key from a file. If not found, generates and saves a new one."""
    if os.path.exists(path):
        with open(path, "rb") as key_file:
            return key_file.read()
    else:
        print(f"Key not found at {path}. Generating a new key.")
        new_key = generate_key_bytes()
        save_key(new_key, path)
        return new_key

# --- Initialize Cipher Suite ---
# Load the key and initialize Fernet instance when the module is loaded.
# This makes it available for encrypt/decrypt functions.
try:
    ENCRYPTION_KEY = load_key_bytes()
    if not ENCRYPTION_KEY: # Should not happen with current load_key_bytes logic
        raise ValueError("Failed to load or generate encryption key.")
    cipher_suite = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"Critical error during encryption module initialization: {e}")
    # Fallback or raise - for now, print and subsequent calls will fail if cipher_suite is not set
    cipher_suite = None 

# --- Encryption/Decryption Functions ---
def encrypt_data(data_dict):
    """Encrypts a dictionary after converting it to a JSON string."""
    if cipher_suite is None:
        raise RuntimeError("Encryption service not initialized properly (cipher_suite is None).")
    try:
        json_string = json.dumps(data_dict)
        bytes_to_encrypt = json_string.encode('utf-8')
        encrypted_bytes = cipher_suite.encrypt(bytes_to_encrypt)
        return encrypted_bytes
    except Exception as e:
        print(f"Error during encryption: {e}")
        return None # Or raise a custom exception

def decrypt_data(encrypted_bytes):
    """Decrypts bytes back into a dictionary (via JSON string)."""
    if cipher_suite is None:
        raise RuntimeError("Encryption service not initialized properly (cipher_suite is None).")
    try:
        decrypted_bytes = cipher_suite.decrypt(encrypted_bytes)
        json_string = decrypted_bytes.decode('utf-8')
        data_dict = json.loads(json_string)
        return data_dict
    except Exception as e: # Includes InvalidToken if decryption fails
        print(f"Error during decryption (data may be corrupted or key mismatch): {e}")
        return None # Or raise a custom exception

if __name__ == '__main__':
    print("--- Encryption Module Test ---")
    
    # Ensure key is loaded/generated
    print(f"Encryption Key loaded/generated from: {KEY_PATH}")
    if ENCRYPTION_KEY:
        print(f"Key (first 10 bytes): {ENCRYPTION_KEY[:10]}...")
    else:
        print("ENCRYPTION_KEY is None after load_key_bytes call.") # Should not happen

    if cipher_suite:
        print("Cipher suite initialized successfully.")
        
        sample_bet = {"type": "number", "value": "17", "amount": 100}
        print(f"Original data: {sample_bet}")
        
        encrypted = encrypt_data(sample_bet)
        if encrypted:
            print(f"Encrypted data (first 20 bytes): {encrypted[:20]}...")
            
            decrypted = decrypt_data(encrypted)
            if decrypted:
                print(f"Decrypted data: {decrypted}")
                assert decrypted == sample_bet, "Decryption did not match original!"
                print("Encryption/Decryption test PASSED.")
            else:
                print("Decryption FAILED.")
        else:
            print("Encryption FAILED.")
            
        print("Testing decryption with invalid token (simulated):")
        invalid_token = b'gAAAAABl_invalid_token_example_just_random_bytes_for_testing_purpose_GARBAGEGARBAGEGARBAGEGARBAGE=='
        decrypted_invalid = decrypt_data(invalid_token)
        if decrypted_invalid is None:
            print("Decryption of invalid token correctly failed (returned None).")
        else:
            print(f"Decryption of invalid token unexpectedly returned: {decrypted_invalid}")

    else:
        print("Cipher suite NOT initialized. Cannot run tests.")

    # Test key file persistence
    print("Verifying key file persistence...")
    if os.path.exists(KEY_PATH):
        print(f"Key file '{KEY_PATH}' exists.")
        key_content_on_disk = open(KEY_PATH, 'rb').read()
        if key_content_on_disk == ENCRYPTION_KEY:
            print("Content of key file on disk matches loaded key.")
        else:
            print("WARNING: Content of key file on disk does NOT match loaded key!")
    else:
        print(f"Key file '{KEY_PATH}' does NOT exist. This should not happen if load_key_bytes worked.")
