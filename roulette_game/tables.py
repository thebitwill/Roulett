import sqlite3
from roulette_game.database import get_db_connection, initialize_database as initialize_db_tables

# --- Admin Functions for Table Management (Database Driven) ---

def create_table(table_id, name, min_bet, max_bet):
    """
    Creates a new table configuration in the database.

    Args:
        table_id (str): The unique identifier for the table (e.g., "table1").
        name (str): A descriptive name for the table (e.g., "Main Floor - Table 1").
        min_bet (float): The minimum bet amount allowed at this table.
        max_bet (float): The maximum bet amount allowed at this table.

    Returns:
        bool: True if the table was created successfully, False otherwise.
    """
    if not isinstance(min_bet, (int, float)) or not isinstance(max_bet, (int, float)):
        print("Error: Minimum and maximum bet must be numbers.")
        return False
    if min_bet <= 0:
        print("Error: Minimum bet must be positive.")
        return False
    if max_bet <= min_bet:
        print("Error: Maximum bet must be greater than minimum bet.")
        return False

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO game_tables (table_id, name, min_bet, max_bet) VALUES (?, ?, ?, ?)",
                           (table_id, name, min_bet, max_bet))
            conn.commit()
            print(f"Table '{name}' (ID: {table_id}) created with min_bet: {min_bet}, max_bet: {max_bet}.")
            return True
    except sqlite3.IntegrityError: # Handles PRIMARY KEY constraint violation (table_id exists)
        print(f"Error: Table ID '{table_id}' already exists.")
        return False
    except sqlite3.Error as e:
        print(f"Database error creating table '{table_id}': {e}")
        return False

def get_table(table_id):
    """
    Retrieves the configuration for a specific table from the database.

    Args:
        table_id (str): The ID of the table to retrieve.

    Returns:
        dict or None: The table configuration dictionary if found, otherwise None.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT table_id, name, min_bet, max_bet FROM game_tables WHERE table_id = ?", (table_id,))
            row = cursor.fetchone()
            if row:
                return {"table_id": row[0], "name": row[1], "min_bet": row[2], "max_bet": row[3]}
            else:
                return None
    except sqlite3.Error as e:
        print(f"Database error getting table '{table_id}': {e}")
        return None

def list_tables():
    """
    Returns a list of all configured tables from the database.

    Returns:
        list: A list of dictionaries, where each dictionary represents a table.
              Returns an empty list if no tables are configured or an error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT table_id, name, min_bet, max_bet FROM game_tables")
            rows = cursor.fetchall()
            tables_list = []
            for row in rows:
                tables_list.append({"table_id": row[0], "name": row[1], "min_bet": row[2], "max_bet": row[3]})
            return tables_list
    except sqlite3.Error as e:
        print(f"Database error listing tables: {e}")
        return []

def update_table_limits(table_id, min_bet, max_bet):
    """
    Updates the minimum and maximum bet limits for an existing table in the database.

    Args:
        table_id (str): The ID of the table to update.
        min_bet (float): The new minimum bet amount.
        max_bet (float): The new maximum bet amount.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if not isinstance(min_bet, (int, float)) or not isinstance(max_bet, (int, float)):
        print("Error: Minimum and maximum bet must be numbers.")
        return False
    if min_bet <= 0:
        print("Error: Minimum bet must be positive.")
        return False
    if max_bet <= min_bet:
        print("Error: Maximum bet must be greater than minimum bet.")
        return False

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE game_tables SET min_bet = ?, max_bet = ? WHERE table_id = ?",
                           (min_bet, max_bet, table_id))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Table ID '{table_id}' updated. New min_bet: {min_bet}, max_bet: {max_bet}.")
                return True
            else:
                print(f"Error: Table ID '{table_id}' not found. Cannot update limits.")
                return False
    except sqlite3.Error as e:
        print(f"Database error updating table '{table_id}': {e}")
        return False

if __name__ == '__main__':
    # Initialize the database and tables first (important for a clean test run)
    print("--- Initializing Database for Table Management Demonstration ---")
    initialize_db_tables() # This will also create the casino wallet if not present.

    print("\n--- Table Management Demonstration (DB) ---")
    
    # Create sample tables
    print("\n--- Creating Tables ---")
    create_table("db_table1", "DB High Rollers Lounge", 100.0, 5000.0)
    create_table("db_table2", "DB Casual Corner", 10.0, 200.0)
    create_table("db_table3", "DB Standard Deck", 25.0, 500.0)
    create_table("db_table1", "DB Duplicate Table Attempt", 1.0, 10.0) # Attempt to create duplicate

    print("\n--- Listing Tables ---")
    available_tables = list_tables()
    if available_tables:
        for table_info in available_tables: # Now a list of dicts
            print(f"ID: {table_info['table_id']}, Name: {table_info['name']}, Min: {table_info['min_bet']}, Max: {table_info['max_bet']}")
    else:
        print("No tables configured or error listing tables.")

    print("\n--- Getting Specific Table ---")
    specific_table = get_table("db_table2")
    if specific_table:
        print(f"Details for db_table2: {specific_table}")
    else:
        print("Table db_table2 not found.")
        
    non_existent_table = get_table("db_table_unknown")
    if non_existent_table is None:
        print("Correctly returned None for non-existent table 'db_table_unknown'.")


    print("\n--- Updating Table Limits ---")
    update_table_limits("db_table2", 15.0, 250.0) # Valid update
    updated_table2 = get_table("db_table2")
    if updated_table2:
        print(f"Details for db_table2 after update: {updated_table2}")

    update_table_limits("db_table_unknown", 1.0, 5.0) # Table not found
    update_table_limits("db_table3", 50.0, 20.0) # Invalid limits (max < min)
    update_table_limits("db_table3", -5.0, 20.0) # Invalid limits (min <=0)


    print("\n--- Final Table Configurations (Listing Again) ---")
    final_tables = list_tables()
    if final_tables:
        for table_info in final_tables:
            print(f"ID: {table_info['table_id']}, Name: {table_info['name']}, Min: {table_info['min_bet']}, Max: {table_info['max_bet']}")
    else:
        print("No tables to list.")
    
    print("\n--- Table DB Demonstration Complete ---")
