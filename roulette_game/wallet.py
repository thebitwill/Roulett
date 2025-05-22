# In-memory data structure for user balances
user_balances = {}

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
    if user_id not in user_balances:
        print(f"User '{user_id}' not found. Cannot deposit.")
        return False
    if not isinstance(amount, (int, float)) or amount <= 0:
        print("Deposit amount must be a positive number.")
        return False
    user_balances[user_id] += amount
    print(f"Deposited {amount} into '{user_id}'. New balance: {user_balances[user_id]}")
    return True

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
    Prevents balance from going below zero.
    Args:
        user_id (str): The user's ID.
        amount (int): The amount to adjust by. Positive for credit, negative for debit.
    Returns:
        bool: True if adjustment was successful, False otherwise.
    """
    balance = get_balance(user_id)
    if balance is None:
        print(f"User '{user_id}' not found. Cannot adjust balance.")
        return False
    if not isinstance(amount, (int, float)):
        print("Adjustment amount must be a number.")
        return False
        
    if balance + amount < 0:
        print(f"Adjustment of {amount} for '{user_id}' would result in negative balance. Operation cancelled.")
        # Optionally, set balance to 0 if that's preferred: user_balances[user_id] = 0
        return False
    user_balances[user_id] += amount
    # print(f"Adjusted balance for '{user_id}' by {amount}. New balance: {user_balances[user_id]}") # Can be noisy
    return True

if __name__ == '__main__':
    print("--- Wallet System Demonstration ---")
    create_user("user1", 100)
    create_user("user2") # Initial balance 0
    create_user("user1") # Attempt to create existing user

    print(f"\nUser1 balance: {get_balance('user1')}")
    print(f"User3 balance: {get_balance('user3')}") # Non-existent user

    deposit("user1", 50)
    deposit("user2", 200)
    deposit("user1", -10) # Invalid deposit
    deposit("user3", 100) # Non-existent user

    withdraw("user1", 30)
    withdraw("user2", 250) # Insufficient funds
    withdraw("user1", 200) # Insufficient funds (balance is 120 after 100+50-30)
    withdraw("user1", -5)  # Invalid withdrawal
    withdraw("user3", 10)  # Non-existent user

    print(f"\nUser1 balance before adjust: {get_balance('user1')}") # Should be 120
    adjust_balance("user1", -20) # Debit 20
    print(f"User1 balance after debit: {get_balance('user1')}") # Should be 100
    adjust_balance("user1", 50)  # Credit 50
    print(f"User1 balance after credit: {get_balance('user1')}") # Should be 150
    adjust_balance("user1", -200) # Attempt to make balance negative
    print(f"User1 balance after negative attempt: {get_balance('user1')}") # Should still be 150
    
    adjust_balance("user2", -user_balances["user2"]) # Withdraw all money from user2
    print(f"User2 balance after withdrawing all: {get_balance('user2')}") # Should be 0

    print("\n--- Final Balances ---")
    for user, bal in user_balances.items():
        print(f"{user}: {bal}")
