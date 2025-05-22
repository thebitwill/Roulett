# Data structure for game tables
game_tables = {}

# --- Admin Functions for Table Management ---

def create_table(table_id, name, min_bet, max_bet):
    """
    Creates a new table configuration.

    Args:
        table_id (str): The unique identifier for the table (e.g., "table1").
        name (str): A descriptive name for the table (e.g., "Main Floor - Table 1").
        min_bet (int): The minimum bet amount allowed at this table.
        max_bet (int): The maximum bet amount allowed at this table.

    Returns:
        bool: True if the table was created successfully, False if it already exists or inputs are invalid.
    """
    if table_id in game_tables:
        print(f"Error: Table ID '{table_id}' already exists.")
        return False
    if not isinstance(min_bet, (int, float)) or not isinstance(max_bet, (int, float)):
        print("Error: Minimum and maximum bet must be numbers.")
        return False
    if min_bet <= 0:
        print("Error: Minimum bet must be positive.")
        return False
    if max_bet <= min_bet:
        print("Error: Maximum bet must be greater than minimum bet.")
        return False

    game_tables[table_id] = {
        "name": name,
        "min_bet": min_bet,
        "max_bet": max_bet,
        # Future: "payout_multipliers": {} # Placeholder for table-specific multipliers
    }
    print(f"Table '{name}' (ID: {table_id}) created with min_bet: {min_bet}, max_bet: {max_bet}.")
    return True

def get_table(table_id):
    """
    Retrieves the configuration for a specific table.

    Args:
        table_id (str): The ID of the table to retrieve.

    Returns:
        dict or None: The table configuration dictionary if found, otherwise None.
    """
    return game_tables.get(table_id)

def list_tables():
    """
    Returns a list of available table IDs and their names.

    Returns:
        list: A list of tuples, where each tuple is (table_id, table_name).
              Returns an empty list if no tables are configured.
    """
    if not game_tables:
        return []
    return [(tid, details["name"]) for tid, details in game_tables.items()]

def update_table_limits(table_id, min_bet, max_bet):
    """
    Updates the minimum and maximum bet limits for an existing table.

    Args:
        table_id (str): The ID of the table to update.
        min_bet (int): The new minimum bet amount.
        max_bet (int): The new maximum bet amount.

    Returns:
        bool: True if the update was successful, False otherwise (e.g., table not found, invalid limits).
    """
    table = get_table(table_id)
    if not table:
        print(f"Error: Table ID '{table_id}' not found. Cannot update limits.")
        return False
    if not isinstance(min_bet, (int, float)) or not isinstance(max_bet, (int, float)):
        print("Error: Minimum and maximum bet must be numbers.")
        return False
    if min_bet <= 0:
        print("Error: Minimum bet must be positive.")
        return False
    if max_bet <= min_bet:
        print("Error: Maximum bet must be greater than minimum bet.")
        return False

    table["min_bet"] = min_bet
    table["max_bet"] = max_bet
    print(f"Table '{table['name']}' (ID: {table_id}) updated. New min_bet: {min_bet}, max_bet: {max_bet}.")
    return True

if __name__ == '__main__':
    print("--- Table Management Demonstration ---")
    
    # Create sample tables
    create_table("table1", "High Rollers Lounge", 100, 5000)
    create_table("table2", "Casual Corner", 10, 200)
    create_table("table3", "Standard Deck", 25, 500)
    create_table("table1", "Duplicate Table", 1, 10) # Attempt to create duplicate

    print("\n--- Listing Tables ---")
    available_tables = list_tables()
    if available_tables:
        for tid, name in available_tables:
            print(f"ID: {tid}, Name: {name}, Config: {get_table(tid)}")
    else:
        print("No tables configured.")

    print("\n--- Updating Table Limits ---")
    update_table_limits("table2", 15, 250) # Valid update
    update_table_limits("table_unknown", 1, 5) # Table not found
    update_table_limits("table3", 50, 20) # Invalid limits (max < min)
    update_table_limits("table3", -5, 20) # Invalid limits (min <=0)


    print("\n--- Final Table Configurations ---")
    for tid, name in list_tables():
        print(f"ID: {tid}, Name: {name}, Config: {get_table(tid)}")

    # Example of getting a single table
    print("\n--- Get Specific Table ---")
    high_roller_table = get_table("table1")
    if high_roller_table:
        print(f"Details for table1: {high_roller_table}")
    else:
        print("Table table1 not found.")
