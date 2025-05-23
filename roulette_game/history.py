import datetime

# Data structure for round history
round_history = {}  # Key: round_id, Value: {"table_id": ..., "winning_slot": ..., "timestamp": ...}

# Data structure for pending bets (bets placed before a round's result)
pending_bets = {}  # Key: round_id, Value: list of bet objects

def record_round_result(round_id, table_id, winning_slot):
    """
    Records the result of a completed round.

    Args:
        round_id (str): The unique ID of the round.
        table_id (str): The ID of the table where the round was played.
        winning_slot (dict): The winning slot dictionary (e.g., {"value": "7", "color": "red"}).
    """
    if round_id in round_history:
        print(f"Warning: Round ID '{round_id}' already has a recorded result. Overwriting.")
    
    round_history[round_id] = {
        "table_id": table_id,
        "winning_slot": winning_slot,
        "timestamp": datetime.datetime.now().isoformat()
    }
    print(f"History: Round {round_id} result recorded: {winning_slot['value']} ({winning_slot['color']}) for table {table_id}.")

def get_round_info(round_id):
    """
    Retrieves the stored information for a given round_id.

    Args:
        round_id (str): The ID of the round to retrieve.

    Returns:
        dict or None: The round information if found, otherwise None.
    """
    return round_history.get(round_id)

def store_bet_for_round(round_id, bet_details):
    """
    Stores a user's bet for an upcoming round.

    Args:
        round_id (str): The ID of the round for which the bet is placed.
        bet_details (dict): A dictionary containing bet information.
                           (e.g., {"user_id": "user1", "bet_type": "number", 
                                   "value": "10", "amount": 5, 
                                   "encrypted_bet": "conceptually_encrypted_data"})
    """
    if round_id not in pending_bets:
        pending_bets[round_id] = []
    pending_bets[round_id].append(bet_details)
    # print(f"Bet stored for round {round_id}: User {bet_details['user_id']} bet {bet_details['amount']} on {bet_details['type']} {bet_details['value']}.")

def get_bets_for_round(round_id):
    """
    Retrieves all bets stored for a given round_id.

    Args:
        round_id (str): The ID of the round.

    Returns:
        list: A list of bet dictionaries for the round. Returns an empty list if no bets.
    """
    return pending_bets.get(round_id, [])

def clear_bets_for_round(round_id):
    """
    Clears all pending bets for a given round_id after they have been processed.

    Args:
        round_id (str): The ID of the round whose bets should be cleared.
    """
    if round_id in pending_bets:
        del pending_bets[round_id]
        # print(f"Pending bets for round {round_id} cleared.")

if __name__ == '__main__':
    print("--- History and Pending Bets Demonstration ---")

    # Test record_round_result and get_round_info
    test_round_id_1 = "tableA_20231027100000_1" # Using a more structured ID
    test_winning_slot_1 = {"value": "10", "color": "black"}
    record_round_result(test_round_id_1, "tableA", test_winning_slot_1)

    test_round_id_2 = "tableB_20231027100005_1"
    test_winning_slot_2 = {"value": "0", "color": "green"}
    record_round_result(test_round_id_2, "tableB", test_winning_slot_2)

    print(f"\nInfo for round {test_round_id_1}: {get_round_info(test_round_id_1)}")
    print(f"Info for round {test_round_id_2}: {get_round_info(test_round_id_2)}")
    print(f"Info for non-existent round: {get_round_info('non_existent_round')}")

    # Test store_bet_for_round and get_bets_for_round
    bet1_round1 = {"user_id": "user1", "bet_type": "number", "value": "10", "amount": 5, "encrypted_bet": "enc_data_1"}
    bet2_round1 = {"user_id": "user2", "bet_type": "color", "value": "red", "amount": 10, "encrypted_bet": "enc_data_2"}
    
    store_bet_for_round(test_round_id_1, bet1_round1)
    store_bet_for_round(test_round_id_1, bet2_round1)

    bet1_round2 = {"user_id": "user3", "bet_type": "even_odd", "value": "even", "amount": 7, "encrypted_bet": "enc_data_3"}
    store_bet_for_round(test_round_id_2, bet1_round2)

    print(f"\nBets for round {test_round_id_1}: {get_bets_for_round(test_round_id_1)}")
    print(f"Bets for round {test_round_id_2}: {get_bets_for_round(test_round_id_2)}")
    print(f"Bets for non-existent round: {get_bets_for_round('non_existent_round')}")

    # Test clear_bets_for_round
    clear_bets_for_round(test_round_id_1)
    print(f"\nBets for round {test_round_id_1} after clearing: {get_bets_for_round(test_round_id_1)}")
    print(f"Pending bets structure after clearing one round: {pending_bets}")

    clear_bets_for_round(test_round_id_2)
    print(f"Pending bets structure after clearing all test rounds: {pending_bets}")
