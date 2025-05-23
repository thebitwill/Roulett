# This file will contain functions for placing bets and determining winners.
import uuid
import datetime
from roulette_game.wheel import spin_wheel, CURRENT_WHEEL as ACTIVE_WHEEL 
# For Subtask 6, wallet.py does not yet have CASINO_WALLET_ID or initialize_casino_wallet
# The adjust_balance used here is the one from Subtask 4 (no casino mirroring).
from roulette_game.wallet import get_balance, adjust_balance, create_user, deposit 
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
        return False 

    table_config = get_table(table_id)
    if table_config is None:
        print(f"Error: Table '{table_id}' not found. Cannot place bet.")
        return False

    min_bet = table_config["min_bet"]
    max_bet = table_config["max_bet"]

    bets_placed_this_turn_count = 0
    while True: 
        print(f"\nPlace your bet for round {round_id}, {user_id}, at table '{table_config['name']}' (Balance: {current_balance}).")
        print(f"Table limits: Min Bet: {min_bet}, Max Bet: {max_bet}.")
        
        bet_amount_val = None
        while True: # Loop for getting valid bet amount
            try:
                amount_input_str = input(f"Enter bet amount (or 0 to finish betting for this round for user {user_id}): ")
                bet_amount_val = int(amount_input_str)
                if bet_amount_val == 0:
                    break 
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
                break 
            except ValueError:
                print("Invalid amount. Please enter a number.")
        
        if bet_amount_val == 0: 
            break 

        bet_type_val = None
        while True: # Loop for getting valid bet type
            bet_type_input_val = input("Choose bet type ('number', 'color', 'even_odd'), or type 'cancel' to cancel this specific bet: ").lower().strip()
            if bet_type_input_val == 'cancel':
                break 
            if bet_type_input_val in ['number', 'color', 'even_odd']:
                bet_type_val = bet_type_input_val
                break
            print("Invalid bet type. Please choose from 'number', 'color', 'even_odd', or 'cancel'.")
        
        if bet_type_input_val == 'cancel':
            if input("Place a different bet instead? (yes/no): ").lower().strip() != 'yes':
                break 
            else:
                continue 

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

        # Debit user's balance (Subtask 4 - wallet.py's adjust_balance does NOT mirror to casino yet)
        if not adjust_balance(user_id, -bet_amount_val):
            print(f"Error: Could not deduct bet amount for {user_id}. Bet not placed.")
            continue 

        bet_details_to_store = {
            "user_id": user_id,
            "type": bet_type_val,
            "value": bet_value_val,
            "amount": bet_amount_val,
            "encrypted_bet": f"conceptually_encrypted_data_for_{user_id}_bet_on_{bet_value_val}" # Subtask 6
        }
        store_bet_for_round(round_id, bet_details_to_store) # Subtask 6
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

# Main round playing function as of end of Subtask 6
# Handles a single user's turn for a round, including placing multiple bets for that round.
def play_round(user_id, table_id): # Name from Subtask 4/5, logic from Subtask 6
    table_config = get_table(table_id) # Subtask 5
    if not table_config:
        print(f"Error: Table '{table_id}' could not be found. Skipping round.")
        return None 

    current_round_id = generate_round_id(table_id) # Subtask 6
    initial_user_balance = get_balance(user_id)
    print(f"\n--- New Round Starting (ID: {current_round_id}) for user {user_id} at '{table_config['name']}' (Balance: {initial_user_balance}) ---")

    # Betting phase for the single user (Subtask 6 allows multiple bets via place_bet's internal loop)
    if not place_bet(user_id, table_id, current_round_id):
        print(f"User {user_id} did not place any bets for round {current_round_id}.")
        print("--- Round End (no bets placed) ---\n")
        # Optionally record this round in history even if no bets, or just return.
        # For now, returning round_id for consistency.
        return current_round_id 
            
    print(f"\n--- Betting phase for round {current_round_id} by user {user_id} ended. ---")
    
    winning_slot = spin_wheel() # Uses CURRENT_WHEEL from wheel.py (Subtask 3)
    print(f"Wheel is spinning for round {current_round_id}...")
    print(f"The wheel landed on: {winning_slot['value']} ({winning_slot['color']})")

    record_round_result(current_round_id, table_id, winning_slot) # Subtask 6

    # Process only this user's bets for this round (Subtask 6)
    # (though place_bet as structured only adds for the current user_id anyway)
    bets_for_this_user_in_round = [
        bet for bet in get_bets_for_round(current_round_id) if bet['user_id'] == user_id
    ]

    if not bets_for_this_user_in_round:
        print(f"No bets were actually stored for user {user_id} in round {current_round_id}.")
    else:
        print(f"\n--- Processing {len(bets_for_this_user_in_round)} bets for user {user_id} in round {current_round_id} ---")
        for bet in bets_for_this_user_in_round:
            payout_multiplier = check_bet(bet, winning_slot) # Returns multiplier (Subtask 4)
            if payout_multiplier > 0:
                winnings_to_credit = payout_multiplier * bet['amount']
                # adjust_balance from Subtask 4 (no casino mirroring yet)
                adjust_balance(bet['user_id'], winnings_to_credit) 
                print(f"User {bet['user_id']}: Bet on {bet['type']} '{bet['value']}' ({bet['amount']}) WON! Received: {winnings_to_credit}. Balance: {get_balance(bet['user_id'])}")
            else:
                print(f"User {bet['user_id']}: Bet on {bet['type']} '{bet['value']}' ({bet['amount']}) lost. Balance: {get_balance(bet['user_id'])}")
    
    clear_bets_for_round(current_round_id) 
    
    final_user_balance = get_balance(user_id)
    print(f"\n--- Round {current_round_id} for user {user_id} at table '{table_config['name']}' ended. ---")
    print(f"{user_id}'s final balance after round: {final_user_balance}")
    print("--- Round End ---\n")
    return current_round_id


if __name__ == '__main__':
    # End of Subtask 6: Demonstrates round management, history, and single player rounds.
    # Casino wallet and multi-user round processing with summaries are for Subtask 7.

    print("--- Admin: Setting up tables (Subtask 6 Demo Style) ---")
    create_game_table("s6_table1", "Subtask 6 Table A", min_bet=5, max_bet=50)
    create_game_table("s6_table2", "Subtask 6 Table B", min_bet=20, max_bet=200)
    print("--- Table setup complete ---\n")

    player_s6_a = "player_S6_Alice"
    player_s6_b = "player_S6_Bob"
    create_user(player_s6_a, 250)
    create_user(player_s6_b, 180)

    # Player Alice plays a round
    print(f"\n>>> Simulating a round for {player_s6_a} at table 's6_table1' <<<")
    r_id_1 = play_round(player_s6_a, "s6_table1")
    if r_id_1:
        print(f"Round {r_id_1} for {player_s6_a} completed. Balance: {get_balance(player_s6_a)}")

    # Player Bob plays a round (this will be a new, separate round)
    print(f"\n>>> Simulating a round for {player_s6_b} at table 's6_table1' <<<")
    r_id_2 = play_round(player_s6_b, "s6_table1")
    if r_id_2:
        print(f"Round {r_id_2} for {player_s6_b} completed. Balance: {get_balance(player_s6_b)}")
    
    # Player Alice plays another round, this time at a different table
    print(f"\n>>> Simulating a round for {player_s6_a} at table 's6_table2' <<<")
    r_id_3 = play_round(player_s6_a, "s6_table2")
    if r_id_3:
        print(f"Round {r_id_3} for {player_s6_a} completed. Balance: {get_balance(player_s6_a)}")


    print("\n--- Conceptual: Storing multiple user bets for a single future round ID (Subtask 6 context) ---")
    # This section demonstrates that multiple bets for different users *can* be stored for the same round_id,
    # even though play_round above processes bets for only the user who initiated that play_round call.
    # The actual processing of a single round with multiple users' bets is a Subtask 7 feature.
    
    shared_round_id = generate_round_id("s6_table1")
    print(f"Generated shared round ID for 's6_table1': {shared_round_id}")
    
    print(f"... {player_s6_a} places bets for shared round {shared_round_id} ...")
    # Simulate placing a bet (user will be prompted)
    place_bet(player_s6_a, "s6_table1", shared_round_id) 
    
    print(f"... {player_s6_b} places bets for shared round {shared_round_id} ...")
    # Simulate placing a bet (user will be prompted)
    place_bet(player_s6_b, "s6_table1", shared_round_id)
    
    print(f"All bets stored for conceptual shared round {shared_round_id}: {get_bets_for_round(shared_round_id)}")
    # These bets are stored but not processed by the play_round calls above.
    # A Subtask 7 function (play_multi_user_round) would process these.
    # For cleanup in this demo:
    clear_bets_for_round(shared_round_id) 
    print(f"Bets for {shared_round_id} cleared for this demo.")


    print("\n--- Viewing Past Round Results (Subtask 6 Demo) ---")
    if r_id_1:
        print(f"Details for Round {r_id_1}: {get_round_info(r_id_1)}")
    if r_id_2:
        print(f"Details for Round {r_id_2}: {get_round_info(r_id_2)}")
    if r_id_3:
        print(f"Details for Round {r_id_3}: {get_round_info(r_id_3)}")
    # For the shared_round_id, a result wasn't recorded as it wasn't "played" by play_round.
    # If it had been, get_round_info(shared_round_id) would show it.


    print("\n--- Final Balances (End of Subtask 6 Demo) ---")
    print(f"{player_s6_a}: {get_balance(player_s6_a)}")
    print(f"{player_s6_b}: {get_balance(player_s6_b)}")
