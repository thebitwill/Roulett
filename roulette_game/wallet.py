# In-memory data structure for user balances
user_balances = {}

# Define the casino wallet ID
CASINO_WALLET_ID = "casino_main_wallet"

def initialize_casino_wallet(initial_balance=1000000):
    """
    Creates or resets the casino wallet with a given balance.
    Should be called once at the start of the application.
    """
    if CASINO_WALLET_ID not in user_balances:
        user_balances[CASINO_WALLET_ID] = initial_balance # Direct initialization
        print(f"Casino wallet '{CASINO_WALLET_ID}' initialized with balance: {initial_balance}.")
    else:
        user_balances[CASINO_WALLET_ID] = initial_balance
        print(f"Casino wallet '{CASINO_WALLET_ID}' already exists. Balance reset to: {initial_balance}.")


def create_user(user_id, initial_balance=0):
    """
    Creates a new user with an initial balance.
    Args:
        user_id (str): The unique identifier for the user.
        initial_balance (int, optional): The starting balance. Defaults to 0.
    Returns:
        bool: True if user was created, False if user already exists.
    """
    if user_id in user_balances:
        print(f"User '{user_id}' already exists.")
        return False
    if initial_balance < 0:
        print("Initial balance cannot be negative.")
        return False
    user_balances[user_id] = initial_balance
    print(f"User '{user_id}' created with balance: {initial_balance}")
    return True

def get_balance(user_id):
    """
    Retrieves the current balance for a user.
    Args:
        user_id (str): The user's ID.
    Returns:
        int or None: The balance if user exists, None otherwise.
    """
    if user_id not in user_balances:
        # print(f"User '{user_id}' not found.") # Decided to make it less noisy for internal checks
        return None
    return user_balances[user_id]

def deposit(user_id, amount):
    """
    Deposits funds into a user's account.
    Args:
        user_id (str): The user's ID.
        amount (int): The amount to deposit. Must be positive.
    Returns:
        bool: True if deposit was successful, False otherwise.
    """
    # For regular users, ensure casino wallet is initialized before they are created
    # to correctly mirror initial funding if that were a feature (not currently, but good practice).
    if user_id != CASINO_WALLET_ID and CASINO_WALLET_ID not in user_balances:
        print(f"Warning: Casino wallet not initialized. Initializing with default balance before creating user '{user_id}'.")
        initialize_casino_wallet() # Initialize with default if not done

    if user_id in user_balances:
        print(f"User '{user_id}' already exists. Balance not changed.")
        return False
    if initial_balance < 0:
        print("Initial balance cannot be negative.")
        return False
    user_balances[user_id] = initial_balance
    print(f"User '{user_id}' created with balance: {initial_balance}")
    return True

def get_balance(user_id):
    """
    Retrieves the current balance for a user.
    Args:
        user_id (str): The user's ID.
    Returns:
        int or None: The balance if user exists, None otherwise.
    """
    if user_id not in user_balances:
        # print(f"User '{user_id}' not found.") 
        return None
    return user_balances[user_id]

def deposit(user_id, amount):
    """
    Deposits funds into a user's account.
    This will DECREASE the casino's balance.
    Args:
        user_id (str): The user's ID.
        amount (int): The amount to deposit. Must be positive.
    Returns:
        bool: True if deposit was successful, False otherwise.
    """
    if user_id == CASINO_WALLET_ID:
        print("Cannot deposit directly to casino wallet using this function. Use adjust_balance.")
        return False
    if user_id not in user_balances:
        # Allow creating user on first deposit
        print(f"User '{user_id}' not found. Creating user with deposit amount.")
        if not isinstance(amount, (int, float)) or amount <= 0:
            print("Deposit amount must be a positive number.")
            return False
        create_user(user_id, 0) # Create user with 0, then adjust
    elif not isinstance(amount, (int, float)) or amount <= 0: # Existing user, invalid amount
        print("Deposit amount must be a positive number.")
        return False
    
    # Use adjust_balance to ensure casino mirroring
    if adjust_balance(user_id, amount):
        print(f"Deposited {amount} into '{user_id}'. New balance: {user_balances[user_id]}")
        return True
    else:
        # adjust_balance would have printed an error
        return False


def withdraw(user_id, amount):
    """
    Withdraws funds from a user's account.
    Args:
        user_id (str): The user's ID.
        amount (int): The amount to withdraw. Must be positive and not exceed balance.
    Returns:
        bool: True if withdrawal was successful, False otherwise.
    """
    balance = get_balance(user_id)
    if balance is None:
        print(f"User '{user_id}' not found. Cannot withdraw.")
        return False
    if not isinstance(amount, (int, float)) or amount <= 0:
        print("Withdrawal amount must be a positive number.")
        return False
    if amount > balance:
        print(f"Insufficient funds for '{user_id}'. Requested: {amount}, Available: {balance}")
        return False
    user_balances[user_id] -= amount
    print(f"Withdrew {amount} from '{user_id}'. New balance: {user_balances[user_id]}")
    return True

def adjust_balance(user_id, amount):
    """
    Adjusts a user's balance by a given amount (can be positive or negative).
    Prevents balance from going below zero for regular users.
    Casino wallet can go negative.
    If amount is a debit from user (amount < 0), casino is credited.
    If amount is a credit to user (amount > 0), casino is debited.

    Args:
        user_id (str): The user's ID.
        amount (int): The amount to adjust by. Positive for credit, negative for debit.
    Returns:
        bool: True if adjustment was successful, False otherwise.
    """
    """
    Withdraws funds from a user's account.
    This will INCREASE the casino's balance.
    Args:
        user_id (str): The user's ID.
        amount (int): The amount to withdraw. Must be positive and not exceed balance.
    Returns:
        bool: True if withdrawal was successful, False otherwise.
    """
    if user_id == CASINO_WALLET_ID:
        print("Cannot withdraw directly from casino wallet using this function. Use adjust_balance.")
        return False
        
    # Check if user exists and has sufficient funds BEFORE calling adjust_balance
    # to provide a more specific error than adjust_balance might.
    balance = get_balance(user_id)
    if balance is None:
        print(f"User '{user_id}' not found. Cannot withdraw.")
        return False
    if not isinstance(amount, (int, float)) or amount <= 0:
        print("Withdrawal amount must be a positive number.")
        return False
    if amount > balance:
        print(f"Insufficient funds for '{user_id}'. Requested: {amount}, Available: {balance}")
        return False

    # Use adjust_balance to ensure casino mirroring
    if adjust_balance(user_id, -amount): # Negative amount for withdrawal
        print(f"Withdrew {amount} from '{user_id}'. New balance: {user_balances[user_id]}")
        return True
    else:
        # adjust_balance would have printed an error if it failed for other reasons
        return False

def adjust_balance(user_id, amount):
    """
    Adjusts a user's balance by a given amount (can be positive or negative).
    Prevents balance from going below zero for regular users.
    Casino wallet can go negative.
    If amount is a debit from user (amount < 0), casino is credited.
    If amount is a credit to user (amount > 0), casino is debited.

    Args:
        user_id (str): The user's ID.
        amount (int): The amount to adjust by. Positive for credit, negative for debit.
    Returns:
        bool: True if adjustment was successful, False otherwise.
    """
    if user_id == CASINO_WALLET_ID: # Direct adjustment for casino wallet
        if not isinstance(amount, (int, float)):
            print("Casino adjustment amount must be a number.")
            return False
        if CASINO_WALLET_ID not in user_balances: 
             print(f"Warning: Casino wallet '{CASINO_WALLET_ID}' not found during direct adjustment. Initializing with 0.")
             initialize_casino_wallet(0) 
        user_balances[CASINO_WALLET_ID] += amount
        # print(f"Casino wallet '{CASINO_WALLET_ID}' adjusted by {amount}. New balance: {user_balances[CASINO_WALLET_ID]}")
        return True

    # Regular user adjustment
    balance = get_balance(user_id)
    if balance is None:
        # Handle case where user might be created on first financial interaction if amount is positive
        if amount > 0: # e.g. a direct credit or first deposit before formal creation
            print(f"User '{user_id}' not found. Creating user with this credit as initial balance.")
            create_user(user_id, 0) # create with 0, then the amount will be added
            balance = 0
        else: # Negative amount for non-existent user is an error
            print(f"User '{user_id}' not found. Cannot apply debit.")
            return False
            
    if not isinstance(amount, (int, float)):
        print("Adjustment amount must be a number.")
        return False
        
    if balance + amount < 0:
        print(f"Adjustment of {amount} for '{user_id}' would result in negative balance. Operation cancelled.")
        return False
        
    user_balances[user_id] += amount
    # print(f"Adjusted balance for '{user_id}' by {amount}. New balance: {user_balances[user_id]}")

    # Mirror adjustment to casino wallet
    if CASINO_WALLET_ID not in user_balances:
        print(f"CRITICAL: Casino wallet '{CASINO_WALLET_ID}' not initialized. Initializing with default before mirroring transaction.")
        initialize_casino_wallet() 

    if amount < 0: # User was debited (e.g. placed a bet or withdrew)
        casino_credit = abs(amount)
        user_balances[CASINO_WALLET_ID] += casino_credit
        # print(f"Casino wallet credited by {casino_credit} due to transaction with '{user_id}'. Casino balance: {get_balance(CASINO_WALLET_ID)}")
    elif amount > 0: # User was credited (e.g. winnings or deposit)
        casino_debit = amount
        user_balances[CASINO_WALLET_ID] -= casino_debit
        # print(f"Casino wallet debited by {casino_debit} due to transaction with '{user_id}'. Casino balance: {get_balance(CASINO_WALLET_ID)}")
        
    return True

if __name__ == '__main__':
    print("--- Wallet System Demonstration with Casino Wallet ---")
    initialize_casino_wallet() # Initialize casino with default 1,000,000

    create_user("player1", 100)
    create_user("player2", 50)
    
    print(f"\nInitial Balances:")
    print(f"Player1: {get_balance('player1')}")
    print(f"Player2: {get_balance('player2')}")
    print(f"Casino ({CASINO_WALLET_ID}): {get_balance(CASINO_WALLET_ID)}")

    print("\n--- Player1 deposits 500 ---")
    deposit("player1", 500) # P1: 100+500=600, Casino: 1M-500 = 999500
    print(f"Player1 after deposit: {get_balance('player1')}") 
    print(f"Casino after player1 deposit: {get_balance(CASINO_WALLET_ID)}")

    print("\n--- Player1 places a bet of 10 (simulated by adjust_balance) ---")
    adjust_balance("player1", -10) # P1: 600-10=590, Casino: 999500+10 = 999510
    print(f"Player1 after bet: {get_balance('player1')}") 
    print(f"Casino after player1 bet: {get_balance(CASINO_WALLET_ID)}")

    print("\n--- Player2 places a bet of 20 (simulated by adjust_balance) ---")
    adjust_balance("player2", -20) # P2: 50-20=30, Casino: 999510+20 = 999530
    print(f"Player2 after bet: {get_balance('player2')}") 
    print(f"Casino after player2 bet: {get_balance(CASINO_WALLET_ID)}") 

    print("\n--- Player1 wins 350 (simulated by adjust_balance for winnings) ---")
    # Payout is 350 (e.g. bet 10, won 340 profit + 10 stake back, so 350 credit)
    adjust_balance("player1", 350) # P1: 590+350=940, Casino: 999530-350 = 999180
    print(f"Player1 after win: {get_balance('player1')}") 
    print(f"Casino after player1 win: {get_balance(CASINO_WALLET_ID)}")

    print("\n--- Player2 withdraws 5 ---")
    withdraw("player2", 5) # P2: 30-5=25, Casino: 999180+5 = 999185
    print(f"Player2 after withdraw: {get_balance('player2')}")
    print(f"Casino after player2 withdraw: {get_balance(CASINO_WALLET_ID)}")

    print("\n--- Casino Wallet Direct Adjustment (e.g. operational costs) ---")
    adjust_balance(CASINO_WALLET_ID, -1000) # Casino: 999185-1000 = 998185
    print(f"Casino after direct debit: {get_balance(CASINO_WALLET_ID)}")

    print("\n--- Final Balances ---")
    for user_id_in_system in list(user_balances.keys()): 
        print(f"{user_id_in_system}: {get_balance(user_id_in_system)}")
