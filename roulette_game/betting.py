# This file will contain functions for placing bets and determining winners.
import uuid
import datetime
from roulette_game.wheel import spin_wheel, CURRENT_WHEEL as ACTIVE_WHEEL
# Subtask 7: Import casino wallet functionalities
from roulette_game.wallet import get_balance, adjust_balance, create_user, deposit, initialize_casino_wallet, CASINO_WALLET_ID
from roulette_game.tables import get_table, list_tables as list_game_tables, create_table as create_game_table
from roulette_game.history import (
    record_round_result, get_round_info, 
    store_bet_for_round, get_bets_for_round, clear_bets_for_round
)

# --- Round ID Generation (Subtask 6) ---
def generate_round_id(table_id):
    """
    Generates a unique round ID using table_id and UUID.
    """
    return f"{table_id}_{uuid.uuid4()}"

# --- Betting Logic (Incorporates Subtasks 2, 3, 4, 5, 6) ---
def place_bet(user_id, table_id, round_id):
    """
    Prompts the user to choose a bet type, value, and amount.
    Checks if the user has sufficient balance and if the bet respects table limits.
    Stores the bet in pending_bets for the given round_id after debiting the user.
    Allows user to place multiple bets in one go or skip betting.
    """
    current_balance = get_balance(user_id)
    if current_balance is None:
        print(f"User '{user_id}' not found. Cannot place bet.")
        return False # Indicates no bet was placed

    table_config = get_table(table_id)
    if table_config is None:
        print(f"Error: Table '{table_id}' not found. Cannot place bet.")
        return False

    min_bet = table_config["min_bet"]
    max_bet = table_config["max_bet"]

    bets_placed_this_turn_count = 0
    while True: # Loop for placing multiple bets
        print(f"\nPlace your bet for round {round_id}, {user_id}, at table '{table_config['name']}' (Balance: {current_balance}).")
        print(f"Table limits: Min Bet: {min_bet}, Max Bet: {max_bet}.")
        
        # Get bet amount
        bet_amount_val = None
        while True: # Loop for getting valid bet amount
            try:
                amount_input_str = input(f"Enter bet amount (or 0 to finish betting for this round for user {user_id}): ")
                bet_amount_val = int(amount_input_str)
                if bet_amount_val == 0:
                    break # User wants to skip or finish this betting session
                if bet_amount_val < 0:
                    print("Bet amount must be positive.")
                    continue 
                if bet_amount_val > current_balance:
                    print(f"Insufficient balance. You have {current_balance}, but tried to bet {bet_amount_val}.")
                    continue
                if bet_amount_val < min_bet:
                    print(f"Bet amount {bet_amount_val} is below table minimum of {min_bet}.")
                    continue
                if bet_amount_val > max_bet:
                    print(f"Bet amount {bet_amount_val} is above table maximum of {max_bet}.")
                    continue
                break # Bet amount is valid
            except ValueError:
                print("Invalid amount. Please enter a number.")
        
        if bet_amount_val == 0: # User chose to finish betting
            break 

        # Get bet type
        bet_type_val = None
        while True: # Loop for getting valid bet type
            bet_type_input_val = input("Choose bet type ('number', 'color', 'even_odd'), or type 'cancel' to cancel this specific bet: ").lower().strip()
            if bet_type_input_val == 'cancel':
                break # Cancel this specific bet attempt
            if bet_type_input_val in ['number', 'color', 'even_odd']:
                bet_type_val = bet_type_input_val
                break
            print("Invalid bet type. Please choose from 'number', 'color', 'even_odd', or 'cancel'.")
        
        if bet_type_input_val == 'cancel':
            if input("Place a different bet instead? (yes/no): ").lower().strip() != 'yes':
                break # Finish betting for this user this round
            else:
                continue # Restart loop for a new bet

        # Get bet value
        bet_value_val = None
        if bet_type_val == 'number':
            while True:
                try:
                    value_input_val = input(f"Enter a number to bet on (e.g., 0, 00, 1-36): ").strip()
                    if any(slot['value'] == value_input_val for slot in ACTIVE_WHEEL):
                        bet_value_val = value_input_val
                        break
                    else:
                        valid_numbers_list_val = sorted(list(set(s['value'] for s in ACTIVE_WHEEL)))
                        valid_numbers_str = ", ".join(valid_numbers_list_val)
                        print(f"Invalid number. Please enter a valid number from the wheel: {valid_numbers_str}")
                except ValueError:
                    print("Invalid input. Please enter a number or zero-variant (0, 00, etc.).")
        elif bet_type_val == 'color':
            while True:
                value_input_val = input("Enter color to bet on ('red' or 'black'): ").lower().strip()
                if value_input_val in ['red', 'black']:
                    bet_value_val = value_input_val
                    break
                print("Invalid color. Please choose 'red' or 'black'.")
        elif bet_type_val == 'even_odd':
            while True:
                value_input_val = input("Enter 'even' or 'odd': ").lower().strip()
                if value_input_val in ['even', 'odd']:
                    bet_value_val = value_input_val
                    break
                print("Invalid choice. Please enter 'even' or 'odd'.")

        # Debit user's balance (Subtask 4 - wallet.py's adjust_balance does NOT yet mirror to casino)
        if not adjust_balance(user_id, -bet_amount_val):
            print(f"Error: Could not deduct bet amount for {user_id}. Bet not placed.")
            continue 

        bet_details_to_pass_to_history = {
            "user_id": user_id,
            "type": bet_type_val,
            "value": bet_value_val,
            "amount": bet_amount_val
            # The "encrypted_bet" placeholder field is REMOVED.
            # history.py's store_bet_for_round will handle the actual encryption.
        }
        store_bet_for_round(round_id, bet_details_to_pass_to_history) # Updated for Subtask 8
        current_balance = get_balance(user_id) 
        print(f"Bet of {bet_amount_val} on {bet_type_val} '{bet_value_val}' stored for round {round_id}. Balance now: {current_balance}")
        bets_placed_this_turn_count += 1
        
        if input(f"{user_id}, place another bet for round {round_id}? (yes/no): ").lower().strip() != 'yes':
            break 
            
    return bets_placed_this_turn_count > 0


def check_bet(bet_details, winning_slot): # Signature from Subtask 6
    """
    Determines if a bet is a winner based on its details and the winning slot.
    Returns the payout multiplier (Subtask 4 change).
    Handles various zero slots (Subtask 3 change).
    """
    bet_type = bet_details['type']
    bet_value = bet_details['value']
    # bet_amount = bet_details['amount'] # Amount is used for calculating final payout, not for multiplier
    winning_value = winning_slot['value']
    winning_color = winning_slot['color']

    if bet_type == 'number':
        return 35 if bet_value == winning_value else 0
    elif bet_type == 'color':
        return 1 if bet_value == winning_color else 0
    elif bet_type == 'even_odd':
        # Handles "0", "00", etc. as non-even/odd (Subtask 3)
        if '0' in winning_value and all(c == '0' for c in winning_value): 
            return 0 
        try:
            winning_num_int = int(winning_value)
            is_winning_even = winning_num_int % 2 == 0
            if (bet_value == 'even' and is_winning_even) or \
               (bet_value == 'odd' and not is_winning_even):
                return 1
        except ValueError: 
            return 0             
    return 0 

# Renamed from play_round and refactored for multi-user and round summaries (Subtask 7)
def play_multi_user_round(table_id, list_of_player_user_ids):
    """
    Manages a complete round of roulette for a list of players at a specific table.
    - Generates a round ID.
    - Allows each player to place bets. (Users' balances are debited, casino credited by adjust_balance in place_bet)
    - Spins the wheel and records the result.
    - Processes bets, calculates payouts, and updates user balances. (Users' balances credited, casino debited for wins by adjust_balance)
    - Calculates and prints round summary statistics.
    - Clears processed bets.

    Args:
        table_id (str): The ID of the table where the game is played.
        list_of_player_user_ids (list): A list of user_ids participating.

    Returns:
        str or None: The round_id if the round was played, None otherwise.
    """
    table_config = get_table(table_id)
    if not table_config:
        print(f"Error: Table '{table_id}' could not be found. Skipping round.")
        return None

    current_round_id = generate_round_id(table_id)
    timestamp_start_iso = datetime.datetime.now().isoformat() # Added for Subtask 9b
    print(f"\n--- Starting Round: {current_round_id} at Table: '{table_config['name']}' ---")

    # Betting Phase
    for user_id in list_of_player_user_ids:
        player_balance = get_balance(user_id)
        if player_balance is None:
            print(f"Player {user_id} not found. Skipping their turn to bet.")
            continue
        
        min_bet_for_table = table_config.get("min_bet", 1) 
        if player_balance < min_bet_for_table:
            print(f"Player {user_id} has insufficient balance ({player_balance}) for min bet ({min_bet_for_table}) at this table. Skipping their turn to bet.")
            continue
        
        print(f"\nPlayer {user_id}, it's your turn to bet (Balance: {player_balance}).")
        # place_bet handles its own loop for multiple bets by one user for the current round
        # It now uses the casino-aware adjust_balance from the updated wallet.py
        place_bet(user_id, table_id, current_round_id) 

    print(f"\n--- Betting phase for round {current_round_id} ended. ---")

    current_round_bets = get_bets_for_round(current_round_id)
    if not current_round_bets: 
        print(f"No bets were placed by any player for round {current_round_id}. Round concluded without a spin.")
        winning_slot = spin_wheel() 
        print(f"Wheel is spinning for round {current_round_id}...")
        print(f"The wheel landed on: {winning_slot['value']} ({winning_slot['color']})")
        record_round_result(current_round_id, table_id, winning_slot, timestamp_start_iso) # Added timestamp_start_iso
        print("\n--- Round Summary ---")
        print(f"Round ID: {current_round_id}")
        print(f"Winning Slot: {winning_slot['value']} ({winning_slot['color']})")
        print(f"Total Amount Staked by Players this Round: 0")
        print(f"Total Amount Paid Out to Players this Round: 0")
        print(f"Casino Net Profit/Loss for this Round: 0")
        casino_balance = get_balance(CASINO_WALLET_ID)
        print(f"Casino Wallet Balance After Round: {casino_balance if casino_balance is not None else 'N/A - Casino Wallet Not Initialized?'}")
        clear_bets_for_round(current_round_id) 
        print(f"\n--- Round {current_round_id} at table '{table_config['name']}' ended. ---")
        return current_round_id 

    winning_slot = spin_wheel() 
    print(f"Wheel is spinning for round {current_round_id}...")
    print(f"The wheel landed on: {winning_slot['value']} ({winning_slot['color']})")

    record_round_result(current_round_id, table_id, winning_slot, timestamp_start_iso) # Added timestamp_start_iso

    total_staked_this_round = sum(bet['amount'] for bet in current_round_bets)
    total_winnings_paid_this_round = 0

    print(f"\n--- Processing {len(current_round_bets)} bets for round {current_round_id} ---")
    # current_round_bets from get_bets_for_round should now be decrypted by history.py
    for bet_detail in current_round_bets: 
        payout_multiplier = check_bet(bet_detail, winning_slot) 
        
        if payout_multiplier > 0:
            win_amount = payout_multiplier * bet_detail['amount']
            adjust_balance(bet_detail['user_id'], win_amount) 
            total_winnings_paid_this_round += win_amount
            print(f"User {bet_detail['user_id']}: Bet on {bet_detail['type']} '{bet_detail['value']}' ({bet_detail['amount']}) WON! Received: {win_amount}. Balance: {get_balance(bet_detail['user_id'])}")
        else:
            print(f"User {bet_detail['user_id']}: Bet on {bet_detail['type']} '{bet_detail['value']}' ({bet_detail['amount']}) lost. Balance: {get_balance(bet_detail['user_id'])}")
    
    casino_net_for_round = total_staked_this_round - total_winnings_paid_this_round
    
    print(f"\n--- Round {current_round_id} Summary ---") 
    print(f"Winning Number: {winning_slot['value']} ({winning_slot['color']})") 
    print(f"Total Staked This Round: {total_staked_this_round}")
    print(f"Total Winnings Paid Out This Round: {total_winnings_paid_this_round}")
    print(f"Casino Net for Round: {casino_net_for_round}")
    casino_balance = get_balance(CASINO_WALLET_ID)
    print(f"Casino Wallet Balance After Round: {casino_balance if casino_balance is not None else 'N/A - Casino Wallet Not Initialized?'}")
    
    clear_bets_for_round(current_round_id) 
    
    print(f"\n--- Round {current_round_id} at table '{table_config['name']}' ended. ---")
    return current_round_id

if __name__ == '__main__':
    initialize_casino_wallet() # Subtask 7: Initialize casino wallet

    print("--- Admin: Setting up tables (Subtask 7 Demo Style) ---")
    create_game_table("s7_table1", "Lucky Table", min_bet=10, max_bet=100)
    create_game_table("s7_table2", "Whale Table", min_bet=200, max_bet=2000)
    print("--- Table setup complete ---\n")

    player_ids_s7 = ["player_X", "player_Y", "player_Z"]
    create_user(player_ids_s7[0], 500)
    create_user(player_ids_s7[1], 300)
    create_user(player_ids_s7[2], 60) # Balance to test min bet at s7_table1

    print(f"Initial Casino Balance: {get_balance(CASINO_WALLET_ID)}")
    for p_id in player_ids_s7:
        print(f"Initial Balance for {p_id}: {get_balance(p_id)}")

    # --- Gameplay Simulation ---
    print("\n\n--- SIMULATING ROUND 1 (Table s7_table1: all players) ---")
    round1_id_s7 = play_multi_user_round("s7_table1", player_ids_s7)
    if round1_id_s7:
        print(f"Round 1 ({round1_id_s7}) completed.")
        # Optional: Peek into history.pending_bets to verify encryption (conceptual)
        # This is for testing/verification and would not be in production.
        # from roulette_game import history # For direct inspection
        # print(f"DEBUG: Raw pending bets for {round1_id_s7} in history: {history.pending_bets.get(round1_id_s7, 'Not found or cleared')}")

        for p_id in player_ids_s7: 
             player_bal = get_balance(p_id)
             if player_bal is not None: 
                print(f"Player {p_id} final balance: {player_bal}")
        print(f"Casino balance after round 1: {get_balance(CASINO_WALLET_ID)}")

    print("\n\n--- SIMULATING ROUND 2 (Table s7_table2: player_X only) ---")
    # Ensure player_X has enough for high roller table
    if get_balance(player_ids_s7[0]) < get_table("s7_table2")["min_bet"]:
        print(f"Admin: Topping up {player_ids_s7[0]}'s balance for VIP table.")
        adjust_balance(player_ids_s7[0], get_table("s7_table2")["min_bet"] * 2) 
        print(f"{player_ids_s7[0]} new balance: {get_balance(player_ids_s7[0])}")
    
    round2_id_s7 = play_multi_user_round("s7_table2", [player_ids_s7[0]])
    if round2_id_s7:
        print(f"Round 2 ({round2_id_s7}) completed.")
        player_bal = get_balance(player_ids_s7[0])
        if player_bal is not None:
            print(f"Player {player_ids_s7[0]} final balance: {player_bal}")
        print(f"Casino balance after round 2: {get_balance(CASINO_WALLET_ID)}")
            
    print("\n\n--- SIMULATING ROUND 3 (Table s7_table1: player_Y, player_Z) ---")
    round3_players_s7 = [player_ids_s7[1], player_ids_s7[2]]
    for p_id in round3_players_s7: 
        current_player_balance = get_balance(p_id)
        if current_player_balance is not None and current_player_balance < get_table("s7_table1")["min_bet"]:
             print(f"Admin: Topping up {p_id}'s balance for table s7_table1.")
             adjust_balance(p_id, get_table("s7_table1")["min_bet"] * 2)
             print(f"{p_id} new balance: {get_balance(p_id)}")

    round3_id_s7 = play_multi_user_round("s7_table1", round3_players_s7)
    if round3_id_s7:
        print(f"Round 3 ({round3_id_s7}) completed.")
        for p_id in round3_players_s7:
            player_bal = get_balance(p_id)
            if player_bal is not None:
                print(f"Player {p_id} final balance: {player_bal}")
        print(f"Casino balance after round 3: {get_balance(CASINO_WALLET_ID)}")

    # --- User Viewing Past Round Results ---
    print("\n\n--- View Past Round Results Example ---")
    if round1_id_s7: 
        print(f"Viewing details for Round 1 ({round1_id_s7}): {get_round_info(round1_id_s7)}")
    if round2_id_s7:
        print(f"Viewing details for Round 2 ({round2_id_s7}): {get_round_info(round2_id_s7)}")
    if round3_id_s7:
        print(f"Viewing details for Round 3 ({round3_id_s7}): {get_round_info(round3_id_s7)}")
    
    print("\n--- Final Balances After All Rounds (Subtask 7 Demo) ---")
    for p_id in player_ids_s7:
        player_bal = get_balance(p_id)
        if player_bal is not None:
            print(f"Player {p_id}: {player_bal}")
    print(f"Casino ({CASINO_WALLET_ID}): {get_balance(CASINO_WALLET_ID)}")
