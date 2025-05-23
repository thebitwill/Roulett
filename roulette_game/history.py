import sqlite3
import datetime
from roulette_game.database import get_db_connection, initialize_database as initialize_db_tables # Renamed for clarity
from roulette_game.encryption import encrypt_data, decrypt_data

# In-memory data structures (round_history, pending_bets) are now removed.

def record_round_result(round_id, table_id, winning_slot, timestamp_start):
    """
    Records the result of a completed round in the database.

    Args:
        round_id (str): The unique ID of the round.
        table_id (str): The ID of the table where the round was played.
        winning_slot (dict): The winning slot dictionary (e.g., {"value": "7", "color": "red"}).
        timestamp_start (str): ISO8601 formatted timestamp when the round started.
    """
    timestamp_end = datetime.datetime.now().isoformat()
    winning_slot_value = winning_slot.get('value')
    winning_slot_color = winning_slot.get('color')

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if round_id exists to decide on INSERT or UPDATE (optional, for now assume new)
            # For simplicity, this example assumes a new round_id or will error if it's a duplicate PK.
            # A more robust version might use INSERT OR REPLACE or an UPDATE statement.
            # However, the current DB schema has round_id as PK, so an INSERT for an existing
            # round_id would fail. The betting.py logic should generate unique round_ids.
            
            # First, ensure the round exists with a start time, then update with results.
            # This matches the new requirement for timestamp_start
            cursor.execute("""
                INSERT INTO rounds (round_id, table_id, winning_slot_value, winning_slot_color, timestamp_start, timestamp_end)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(round_id) DO UPDATE SET
                    winning_slot_value = excluded.winning_slot_value,
                    winning_slot_color = excluded.winning_slot_color,
                    timestamp_end = excluded.timestamp_end;
            """, (round_id, table_id, winning_slot_value, winning_slot_color, timestamp_start, timestamp_end))
            conn.commit()
            print(f"DB History: Round {round_id} result recorded/updated: {winning_slot_value} ({winning_slot_color}) for table {table_id}.")
    except sqlite3.Error as e:
        print(f"Database error recording round result for '{round_id}': {e}")

def get_round_info(round_id):
    """
    Retrieves the stored information for a given round_id from the database.

    Args:
        round_id (str): The ID of the round to retrieve.

    Returns:
        dict or None: The round information if found, otherwise None.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT round_id, table_id, winning_slot_value, winning_slot_color, timestamp_start, timestamp_end 
                FROM rounds 
                WHERE round_id = ?
            """, (round_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "round_id": row[0],
                    "table_id": row[1],
                    "winning_slot": {"value": row[2], "color": row[3]},
                    "timestamp_start": row[4],
                    "timestamp_end": row[5]
                }
            else:
                return None
    except sqlite3.Error as e:
        print(f"Database error getting round info for '{round_id}': {e}")
        return None

def store_bet_for_round(round_id, bet_details):
    """
def store_bet_for_round(round_id, bet_details):
    """
    Stores a user's bet for an upcoming round in the database.
    Bet details (type, value, amount) are encrypted.

    Args:
        round_id (str): The ID of the round for which the bet is placed.
        bet_details (dict): A dictionary containing bet information including user_id,
                           type, value, and amount.
    Returns:
        bool: True if successful, False otherwise.
    """
    sensitive_data = {
        "type": bet_details["type"],
        "value": bet_details["value"],
        "amount": bet_details["amount"]
    }
    encrypted_payload_bytes = encrypt_data(sensitive_data)

    if not encrypted_payload_bytes:
        print(f"Error: Could not encrypt bet for user {bet_details['user_id']} in round {round_id}. Bet not stored.")
        return False

    timestamp_placed = datetime.datetime.now().isoformat()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bets (round_id, user_id, encrypted_payload, timestamp_placed)
                VALUES (?, ?, ?, ?)
            """, (round_id, bet_details["user_id"], sqlite3.Binary(encrypted_payload_bytes), timestamp_placed))
            conn.commit()
            # print(f"DB: Encrypted bet stored for round {round_id} for user {bet_details['user_id']}.")
            return True
    except sqlite3.Error as e:
        print(f"Database error storing bet for round '{round_id}', user '{bet_details['user_id']}': {e}")
        return False

def get_bets_for_round(round_id):
    """
    Retrieves and decrypts all bets stored for a given round_id from the database.

    Args:
        round_id (str): The ID of the round.

    Returns:
        list: A list of decrypted bet detail dictionaries for the round.
              Returns an empty list if no bets or if decryption fails for any.
    """
    reconstructed_bets = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, encrypted_payload FROM bets WHERE round_id = ?", (round_id,))
            rows = cursor.fetchall()
            for row in rows:
                user_id = row[0]
                encrypted_payload_bytes = row[1] # This is already bytes from sqlite3.Binary
                
                decrypted_sensitive_data = decrypt_data(encrypted_payload_bytes)
                
                if decrypted_sensitive_data:
                    reconstructed_bet = {
                        "user_id": user_id,
                        **decrypted_sensitive_data
                    }
                    reconstructed_bets.append(reconstructed_bet)
                else:
                    print(f"Error: Could not decrypt bet for user {user_id} in round {round_id}. Bet excluded.")
                    # Consider how to handle partially corrupted data - for now, skip.
    except sqlite3.Error as e:
        print(f"Database error retrieving bets for round '{round_id}': {e}")
    return reconstructed_bets

def clear_bets_for_round(round_id):
    """
    Bets are permanently stored in the database. 
    This function currently does not delete them to preserve history.
    If deletion is required, uncomment the SQL execution.
    """
    print(f"Info: Bets for round '{round_id}' are permanently stored in the database and not cleared by this function.")
    # If actual deletion is needed:
    # try:
    #     with get_db_connection() as conn:
    #         cursor = conn.cursor()
    #         cursor.execute("DELETE FROM bets WHERE round_id = ?", (round_id,))
    #         conn.commit()
    #         print(f"DB: Bets for round {round_id} deleted.")
    # except sqlite3.Error as e:
    #     print(f"Database error clearing bets for round '{round_id}': {e}")
    pass


if __name__ == '__main__':
    print("--- Database History and Encrypted Bets Demonstration ---")
    
    # Initialize database (creates tables if they don't exist)
    initialize_db_tables() 

    # Sample data
    test_table_id = "db_table_hist_1"
    test_round_id = f"{test_table_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Need to ensure the table exists for foreign key constraint on rounds
    # And a user exists for foreign key constraint on bets
    # This would typically be handled by other modules or a setup script.
    # For this standalone test, we add them directly.
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO game_tables (table_id, name, min_bet, max_bet) VALUES (?, ?, ?, ?)",
                           (test_table_id, "History Test Table", 1.0, 100.0))
            cursor.execute("INSERT OR IGNORE INTO users (user_id, username, balance) VALUES (?, ?, ?)",
                           ("user_hist_1", "HistUser1", 100.0))
            cursor.execute("INSERT OR IGNORE INTO users (user_id, username, balance) VALUES (?, ?, ?)",
                           ("user_hist_2", "HistUser2", 200.0))
            # Also ensure the round is pre-inserted with start time before bets are stored
            # This is because betting.py will create the round first, then bets.
            # For this test, we simulate it here.
            ts_start = datetime.datetime.now().isoformat()
            cursor.execute("INSERT OR IGNORE INTO rounds (round_id, table_id, timestamp_start) VALUES (?, ?, ?)",
                           (test_round_id, test_table_id, ts_start))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error in __main__ setup for history test: {e}")


    print(f"\n--- Storing bets for round {test_round_id} ---")
    bet1_orig = {"user_id": "user_hist_1", "type": "number", "value": "23", "amount": 10.0}
    bet2_orig = {"user_id": "user_hist_2", "type": "color", "value": "black", "amount": 20.0}
    
    store_bet_for_round(test_round_id, bet1_orig)
    store_bet_for_round(test_round_id, bet2_orig)

    print(f"\n--- Retrieving and Decrypting bets for round {test_round_id} ---")
    retrieved_bets = get_bets_for_round(test_round_id)
    assert len(retrieved_bets) == 2, "Should retrieve 2 bets"
    for i, bet in enumerate(retrieved_bets):
        print(f"Decrypted Bet {i+1}: {bet}")
        original_bet = bet1_orig if bet["user_id"] == "user_hist_1" else bet2_orig
        assert bet["type"] == original_bet["type"]
        assert bet["value"] == original_bet["value"]
        assert bet["amount"] == original_bet["amount"]
    print("Bet retrieval and decryption successful.")

    print(f"\n--- Recording round result for {test_round_id} ---")
    winning_slot_data = {"value": "23", "color": "red"}
    # timestamp_start was set when round was 'created'
    # We need to fetch it if not passed directly to record_round_result
    # For this test, we use the ts_start defined above.
    record_round_result(test_round_id, test_table_id, winning_slot_data, ts_start)

    print(f"\n--- Retrieving round info for {test_round_id} ---")
    round_info = get_round_info(test_round_id)
    if round_info:
        print(f"Round Info: {round_info}")
        assert round_info["winning_slot"]["value"] == "23"
        assert round_info["winning_slot"]["color"] == "red"
        assert round_info["timestamp_start"] == ts_start
        assert round_info["timestamp_end"] is not None 
    else:
        print("Failed to retrieve round info.")
        
    print(f"\n--- Attempting to clear bets for round {test_round_id} (should just print a message) ---")
    clear_bets_for_round(test_round_id)
    # Verify bets are still there (as clear_bets_for_round does not delete by default now)
    bets_after_clear_attempt = get_bets_for_round(test_round_id)
    assert len(bets_after_clear_attempt) == 2, "Bets should still be present after non-destructive clear."
    print(f"Bets for round {test_round_id} after 'clear' (still present): {len(bets_after_clear_attempt)}")


    print("\n--- Database History Demonstration Complete ---")
