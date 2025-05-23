import sqlite3
from roulette_game.database import get_db_connection, initialize_database as initialize_db_tables
from .auth import register_user # Added for Subtask 10

# Define the casino wallet ID (used as primary key in casino_wallets table)
CASINO_WALLET_ID = "main_casino_wallet" 

def initialize_casino_wallet(initial_balance=1000000.0):
    """
    Ensures the main casino wallet exists in the database, creating it if necessary.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM casino_wallets WHERE wallet_id = ?", (CASINO_WALLET_ID,))
            wallet = cursor.fetchone()
            if wallet is None:
                cursor.execute("INSERT INTO casino_wallets (wallet_id, balance) VALUES (?, ?)",
                               (CASINO_WALLET_ID, initial_balance))
                conn.commit()
                print(f"Casino wallet '{CASINO_WALLET_ID}' initialized with balance: {initial_balance}.")
            else:
                # Optionally update or just confirm existence
                print(f"Casino wallet '{CASINO_WALLET_ID}' already exists with balance: {wallet[0]}.")
    except sqlite3.Error as e:
        print(f"Error initializing casino wallet: {e}")

def create_user(user_id, initial_balance=0.0, username=None, role='user', plain_password=None):
    """
    Creates a new user by calling the registration function in auth.py.
    Args:
        user_id (str): The unique identifier for the user.
        initial_balance (float, optional): The starting balance. Defaults to 0.0.
        username (str, optional): The username. Defaults to user_id if None.
        role (str, optional): The user's role. Defaults to 'user'.
        plain_password (str): The plain text password for the new user.
    Returns:
        bool: True if user registration was successful, False otherwise.
    """
    if username is None:
        username = user_id
    
    if plain_password is None:
        print("Password is required for user creation.")
        return False
        
    # Delegate to auth.register_user which handles hashing and DB insertion
    return register_user(user_id, username, plain_password, role, initial_balance)

def get_balance(user_id):
    """
    Retrieves the current balance for a user or the casino wallet.
    Args:
        user_id (str): The user's ID or casino wallet ID.
    Returns:
        float or None: The balance if user/wallet exists, None otherwise.
    """
    table_to_query = "users" if user_id != CASINO_WALLET_ID else "casino_wallets"
    id_column = "user_id" if user_id != CASINO_WALLET_ID else "wallet_id"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT balance FROM {table_to_query} WHERE {id_column} = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                # print(f"Balance check: '{user_id}' not found in {table_to_query}.")
                return None
    except sqlite3.Error as e:
        print(f"Database error getting balance for '{user_id}': {e}")
        return None

def deposit(user_id, amount):
    """
    """
    Deposits funds into a user's account.
    This involves crediting the user and debiting the casino wallet.
    Args:
        user_id (str): The user's ID.
        amount (float): The amount to deposit. Must be positive.
    Returns:
        bool: True if deposit was successful, False otherwise.
    """
    if user_id == CASINO_WALLET_ID:
        print("Cannot deposit directly to casino wallet using this function. Use adjust_balance for direct casino adjustments.")
        return False
    if not isinstance(amount, (int, float)) or amount <= 0:
        print("Deposit amount must be a positive number.")
        return False
    
    # Check if user exists; if not, adjust_balance will handle it (or fail if it should)
    # No need to create user here, adjust_balance can do that if it's a credit.
    # However, for a deposit, we typically expect the user to exist. Let's check.
    if get_balance(user_id) is None:
        print(f"Deposit failed: User '{user_id}' does not exist.")
        return False

    if adjust_balance(user_id, amount): # This credits user and debits casino
        new_bal = get_balance(user_id)
        print(f"Deposited {amount} into '{user_id}'. New balance: {new_bal}")
        return True
    else:
        print(f"Deposit failed for user '{user_id}'.")
        return False

def withdraw(user_id, amount_to_withdraw):
    """
    Withdraws funds from a user's account.
    This involves debiting the user and crediting the casino wallet.
    Args:
        user_id (str): The user's ID.
        amount_to_withdraw (float): The amount to withdraw. Must be positive.
    Returns:
        bool: True if withdrawal was successful, False otherwise.
    """
    if user_id == CASINO_WALLET_ID:
        print("Cannot withdraw from casino wallet using this function. Use adjust_balance for direct casino adjustments.")
        return False
    if not isinstance(amount_to_withdraw, (int, float)) or amount_to_withdraw <= 0:
        print("Withdrawal amount must be a positive number.")
        return False

    current_balance = get_balance(user_id)
    if current_balance is None:
        print(f"Withdrawal failed: User '{user_id}' not found.")
        return False
    if amount_to_withdraw > current_balance:
        print(f"Insufficient funds for '{user_id}'. Requested: {amount_to_withdraw}, Available: {current_balance}")
        return False

    # Use adjust_balance with a negative amount for the user
    if adjust_balance(user_id, -amount_to_withdraw): # This debits user and credits casino
        new_bal = get_balance(user_id)
        print(f"Withdrew {amount_to_withdraw} from '{user_id}'. New balance: {new_bal}")
        return True
    else:
        print(f"Withdrawal failed for user '{user_id}'.")
        return False

def adjust_balance(user_id, amount_to_adjust):
    """
    Adjusts a user's or casino's balance in the database.
    For player transactions, it mirrors the adjustment to the casino wallet.
    Args:
        user_id (str): The ID of the user or casino wallet.
        amount_to_adjust (float): The amount to adjust by (positive for credit, negative for debit).
    Returns:
        bool: True if successful, False otherwise.
    """
    if not isinstance(amount_to_adjust, (int, float)):
        print("Adjustment amount must be a number.")
        return False

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            is_casino_transaction = (user_id == CASINO_WALLET_ID)
            target_table = "casino_wallets" if is_casino_transaction else "users"
            target_id_column = "wallet_id" if is_casino_transaction else "user_id"

            # Get current balance
            cursor.execute(f"SELECT balance FROM {target_table} WHERE {target_id_column} = ?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                print(f"Adjustment failed: '{user_id}' not found in {target_table}.")
                return False
            current_balance = row[0]

            new_balance = current_balance + amount_to_adjust

            # Prevent player balances from going below zero
            if not is_casino_transaction and new_balance < 0:
                print(f"Adjustment for user '{user_id}' would result in negative balance ({new_balance}). Setting to 0.")
                new_balance = 0.0
                # The actual amount effectively taken from user is current_balance
                effective_player_debit = -current_balance 
            elif amount_to_adjust < 0 : # if it's a debit
                 effective_player_debit = amount_to_adjust
            else: # if it's a credit
                 effective_player_debit = 0 # Not a debit from player perspective for casino mirroring

            # Update target balance
            cursor.execute(f"UPDATE {target_table} SET balance = ? WHERE {target_id_column} = ?", (new_balance, user_id))

            # Casino Mirroring
            if not is_casino_transaction:
                casino_adjustment = 0
                if amount_to_adjust < 0: # Player was debited (e.g. bet, withdrawal)
                    casino_adjustment = abs(effective_player_debit if new_balance == 0 else amount_to_adjust)
                elif amount_to_adjust > 0: # Player was credited (e.g. deposit, winnings)
                    casino_adjustment = -amount_to_adjust
                
                if casino_adjustment != 0:
                    cursor.execute("SELECT balance FROM casino_wallets WHERE wallet_id = ?", (CASINO_WALLET_ID,))
                    casino_row = cursor.fetchone()
                    if casino_row is None:
                        print(f"CRITICAL: Casino wallet '{CASINO_WALLET_ID}' not found for mirroring. Transaction for '{user_id}' completed, but casino not updated.")
                        # This indicates a serious issue if casino wallet isn't there.
                        # Depending on policy, might rollback or log critical error.
                        # For now, we'll proceed with player's transaction committed.
                    else:
                        current_casino_balance = casino_row[0]
                        new_casino_balance = current_casino_balance + casino_adjustment
                        cursor.execute("UPDATE casino_wallets SET balance = ? WHERE wallet_id = ?",
                                       (new_casino_balance, CASINO_WALLET_ID))
            
            conn.commit()
            # print(f"Adjusted balance for '{user_id}' by {amount_to_adjust}. New balance: {new_balance}.")
            # if not is_casino_transaction and casino_adjustment != 0:
            #     print(f"Casino wallet '{CASINO_WALLET_ID}' adjusted by {casino_adjustment}.")
            return True

    except sqlite3.Error as e:
        print(f"Database error adjusting balance for '{user_id}': {e}")
        if conn:
            conn.rollback()
        return False

if __name__ == '__main__':
    # Ensure the database and tables are ready for the demo
    print("--- Wallet System DB Demonstration ---")
    # Ensure DB is initialized for tests.
    # This is important if running this script directly after DB deletion.
    initialize_db_tables() 
    
    # Test initialize_casino_wallet
    print("\n--- Initializing Casino Wallet ---")
    initialize_casino_wallet(500000.0) 
    initialize_casino_wallet() 

    print("\n--- Creating Users (now requires password) ---")
    # Note: User creation success/failure is now mostly tested in auth.py's __main__
    # Here we just ensure the call from wallet.py works.
    create_user("wallet_user1", 100.0, username="WalletUser1", plain_password="password123")
    create_user("wallet_user2", 50.0, username="WalletUser2", plain_password="securepassword")
    create_user("wallet_user_no_pass", 20.0, username="WalletUserNoPass") # Should fail

    print("\n--- Getting Balances ---")
    print(f"WalletUser1 Balance: {get_balance('wallet_user1')}")
    print(f"WalletUser2 Balance: {get_balance('wallet_user2')}")
    print(f"Casino ({CASINO_WALLET_ID}) Balance: {get_balance(CASINO_WALLET_ID)}")
    print(f"NonExistentUser Balance: {get_balance('non_existent_user')}") # Should be None

    print("\n--- WalletUser1 deposits 200 ---")
    deposit("wallet_user1", 200.0)
    print(f"WalletUser1 after deposit: {get_balance('wallet_user1')}") 
    print(f"Casino after WalletUser1 deposit: {get_balance(CASINO_WALLET_ID)}") 

    print("\n--- WalletUser2 withdraws 30 ---")
    withdraw("wallet_user2", 30.0)
    print(f"WalletUser2 after withdrawal: {get_balance('wallet_user2')}") 
    print(f"Casino after WalletUser2 withdrawal: {get_balance(CASINO_WALLET_ID)}") 

    print("\n--- WalletUser1 adjusts balance by -50 (simulated bet) ---")
    adjust_balance("wallet_user1", -50.0) 
    print(f"WalletUser1 after adjustment: {get_balance('wallet_user1')}") 
    print(f"Casino after WalletUser1 adjustment: {get_balance(CASINO_WALLET_ID)}") 

    print("\n--- Casino Wallet Direct Adjustment ---")
    adjust_balance(CASINO_WALLET_ID, -1000.0) 
    print(f"Casino after direct debit: {get_balance(CASINO_WALLET_ID)}") 

    print("\n--- Final Balances (from DB, selected fields) ---")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            print("Users Table:")
            for row in cursor.execute("SELECT user_id, username, balance, role FROM users"):
                print(f"  - {row}")
            print("Casino Wallets Table:")
            for row in cursor.execute("SELECT wallet_id, balance FROM casino_wallets"):
                print(f"  - {row}")
    except sqlite3.Error as e:
        print(f"Error reading final balances: {e}")
        
    print("\n--- Wallet DB Demonstration Complete ---")
