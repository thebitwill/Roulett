# roulette_game/auth.py
import bcrypt
import sqlite3
from .database import get_db_connection, initialize_database

def hash_password(password_text):
    """
    Hashes a plain text password.
    Returns the hashed password as a string (decoded from bytes).
    """
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_text.encode('utf-8'), salt)
    return hashed_password_bytes.decode('utf-8')

def check_password(password_text, hashed_password_text):
    """
    Checks a plain text password against a stored hashed password.
    Both inputs are expected to be strings.
    """
    encoded_password_text = password_text.encode('utf-8')
    encoded_hashed_password_text = hashed_password_text.encode('utf-8')
    return bcrypt.checkpw(encoded_password_text, encoded_hashed_password_text)

def register_user(user_id, username, plain_password, role='user', initial_balance=0.0):
    """
    Registers a new user with a hashed password.
    """
    hashed_pw = hash_password(plain_password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user_id or username already exists
            cursor.execute("SELECT 1 FROM users WHERE user_id = ? OR username = ?", (user_id, username))
            if cursor.fetchone():
                print(f"Registration failed: User ID '{user_id}' or Username '{username}' already exists.")
                return False
                
            cursor.execute("""
                INSERT INTO users (user_id, username, hashed_password, role, balance)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, hashed_pw, role, initial_balance))
            conn.commit()
            print(f"User '{username}' (ID: {user_id}) registered successfully with role '{role}'.")
            return True
    except sqlite3.IntegrityError: # Should be caught by the check above, but as a safeguard
        print(f"Registration failed due to integrity error (user_id or username likely exists): {username}")
        return False
    except sqlite3.Error as e:
        print(f"Database error during user registration for '{username}': {e}")
        return False

def login_user(username, plain_password):
    """
    Logs in a user by verifying their username and password.
    Returns user details (user_id, username, role) upon successful login, None otherwise.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, hashed_password, role 
                FROM users 
                WHERE username = ?
            """, (username,))
            user_record = cursor.fetchone()

            if user_record:
                user_id, db_username, stored_hashed_password, role = user_record
                if check_password(plain_password, stored_hashed_password):
                    print(f"User '{username}' logged in successfully.")
                    return {"user_id": user_id, "username": db_username, "role": role}
                else:
                    print(f"Login failed for '{username}': Incorrect password.")
                    return None
            else:
                print(f"Login failed for '{username}': User not found.")
                return None
    except sqlite3.Error as e:
        print(f"Database error during login for '{username}': {e}")
        return None

if __name__ == '__main__':
    print("--- Auth Module Demonstration ---")
    
    # Initialize database (ensures tables are created)
    # Note: The DB initialization in database.py also adds a default casino wallet.
    print("\n--- Initializing Database (if not already done) ---")
    initialize_database() 

    print("\n--- Registering Users ---")
    # Clean up potential existing test users from previous runs for a cleaner demo
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM users WHERE username IN (?, ?, ?)", ('testuser1', 'testadmin1', 'testuser_failed'))
            conn.commit()
    except sqlite3.Error as e:
        print(f"DB cleanup error: {e}")

    reg_success1 = register_user("uid1", "testuser1", "password123", role="user", initial_balance=50.0)
    print(f"Registration for testuser1: {'Success' if reg_success1 else 'Failed'}")
    
    reg_success_admin = register_user("uid_admin1", "testadmin1", "adminpass", role="admin", initial_balance=1000.0)
    print(f"Registration for testadmin1: {'Success' if reg_success_admin else 'Failed'}")

    reg_success_dup_username = register_user("uid_dup", "testuser1", "newpassword", role="user") # Attempt duplicate username
    print(f"Registration for duplicate username 'testuser1': {'Success' if reg_success_dup_username else 'Failed'}")
    
    reg_success_dup_id = register_user("uid1", "testuser_other", "newpassword", role="user") # Attempt duplicate user_id
    print(f"Registration for duplicate user_id 'uid1': {'Success' if reg_success_dup_id else 'Failed'}")


    print("\n--- Logging In Users ---")
    # Correct login
    login_details1 = login_user("testuser1", "password123")
    if login_details1:
        print(f"Login successful for testuser1: {login_details1}")
    else:
        print("Login failed for testuser1 with correct password (UNEXPECTED).")

    # Incorrect password
    login_details_fail = login_user("testuser1", "wrongpassword")
    if login_details_fail is None:
        print("Login correctly failed for testuser1 with incorrect password.")
    else:
        print(f"Login for testuser1 with incorrect password returned: {login_details_fail} (UNEXPECTED).")

    # Non-existent user
    login_details_nouser = login_user("nouser", "password123")
    if login_details_nouser is None:
        print("Login correctly failed for non-existent user 'nouser'.")
    else:
        print(f"Login for non-existent user returned: {login_details_nouser} (UNEXPECTED).")
        
    # Admin login
    login_details_admin = login_user("testadmin1", "adminpass")
    if login_details_admin:
        print(f"Login successful for testadmin1: {login_details_admin}")
        assert login_details_admin["role"] == "admin"
    else:
        print("Login failed for testadmin1 with correct password (UNEXPECTED).")

    print("\n--- Auth Module Demonstration Complete ---")
