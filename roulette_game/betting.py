# This file will contain functions for placing bets and determining winners.
import uuid
import datetime
from roulette_game.wheel import spin_wheel, CURRENT_WHEEL as ACTIVE_WHEEL # Import necessary items, using ACTIVE_WHEEL to refer to the current config
from roulette_game.wallet import get_balance, adjust_balance, create_user, deposit # Import wallet functions
from roulette_game.tables import get_table, list_tables as list_game_tables, create_table as create_game_table # Import table functions
from roulette_game.history import (
    record_round_result, get_round_info, 
    store_bet_for_round, get_bets_for_round, clear_bets_for_round
)

# --- Round ID Generation ---
def generate_round_id(table_id):
    """
    Generates a unique round ID using table_id and UUID.
    """
    return f"{table_id}_{uuid.uuid4()}"

# --- Betting Logic ---
def place_bet(user_id, table_id, round_id):
    """
    Prompts the user to choose a bet type, value, and amount.
    Checks if the user has sufficient balance and if the bet respects table limits.
    Stores the bet in pending_bets for the given round_id.

    Args:
        user_id (str): The ID of the user placing the bet.
        table_id (str): The ID of the table where the bet is placed.
        round_id (str): The unique ID of the current round.

    Returns:
        bool: True if the bet was successfully placed and stored, False otherwise.
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

    print(f"\nPlace your bet for round {round_id}, {user_id}, at table '{table_config['name']}' (Balance: {current_balance}).")
    print(f"Table limits: Min Bet: {min_bet}, Max Bet: {max_bet}.")

    while True:
        try:
            bet_amount = int(input("Enter bet amount: "))
            if bet_amount <= 0:
                print("Bet amount must be positive.")
            elif bet_amount > current_balance:
                print(f"Insufficient balance. You have {current_balance}, but tried to bet {bet_amount}.")
                return False # User cannot afford this bet, or doesn't want to place another.
            elif bet_amount < min_bet:
                print(f"Bet amount {bet_amount} is below table minimum of {min_bet}.")
            elif bet_amount > max_bet:
                print(f"Bet amount {bet_amount} is above table maximum of {max_bet}.")
            else:
                break # Bet amount is valid
        except ValueError:
            print("Invalid amount. Please enter a number.")
            
    # If user chose not to bet (e.g. by entering 0 or an invalid amount they didn't correct)
    if bet_amount is None: # Should be caught by earlier checks, but as a failsafe.
        return False

    while True:
        bet_type_input = input("Choose bet type ('number', 'color', 'even_odd'), or type 'done' if no more bets for this round: ").lower().strip()
        if bet_type_input == 'done':
            return False # User finished placing bets for this interaction
        if bet_type_input in ['number', 'color', 'even_odd']:
            bet_type = bet_type_input
            break
        print("Invalid bet type. Please choose from 'number', 'color', 'even_odd', or 'done'.")

    bet_value = None
    if bet_type == 'number':
        while True:
            try:
                value_input = input(f"Enter a number to bet on (e.g., 0, 00, 1-36): ").strip()
                # Check if the input is a valid number on the wheel
                if any(slot['value'] == value_input for slot in ACTIVE_WHEEL):
                    bet_value = value_input
                    break
                else:
                    # Dynamically generate the list of valid numbers for the error message
                    valid_numbers_list = sorted(list(set(s['value'] for s in ACTIVE_WHEEL))) # Unique sorted list
                    valid_numbers = ", ".join(valid_numbers_list)
                    print(f"Invalid number. Please enter a valid number from the wheel: {valid_numbers}")
            except ValueError: # This might not be strictly necessary anymore if we are checking against slot values
                print("Invalid input. Please enter a number or zero-variant (0, 00, etc.).")
    elif bet_type == 'color':
        while True:
            value_input = input("Enter color to bet on ('red' or 'black'): ").lower().strip()
            if value_input in ['red', 'black']:
                bet_value = value_input
                break
            print("Invalid color. Please choose 'red' or 'black'.")
    elif bet_type == 'even_odd':
        while True:
            value_input = input("Enter 'even' or 'odd': ").lower().strip()
            if value_input in ['even', 'odd']:
                bet_value = value_input
                break
            print("Invalid choice. Please enter 'even' or 'odd'.")

    # Deduct bet amount from wallet *before* storing the bet
    if not adjust_balance(user_id, -bet_amount):
        print(f"Error: Could not deduct bet amount for {user_id}. Bet not placed.")
        return False

    bet_details = {
        "user_id": user_id,
        "type": bet_type,
        "value": bet_value,
        "amount": bet_amount,
        "encrypted_bet": f"conceptually_encrypted_data_for_{user_id}_bet_on_{bet_value}" # Placeholder
    }
    store_bet_for_round(round_id, bet_details)
    print(f"Bet of {bet_amount} on {bet_type} '{bet_value}' stored for round {round_id}. Balance now: {get_balance(user_id)}")
    return True


def check_bet(bet_details, winning_slot):
    """
    Determines if a bet is a winner and calculates the payout.

    Args:
        bet: A dictionary representing the user's bet 
             (e.g., {'type': 'number', 'value': '17', 'amount': 1}).
        winning_slot: A dictionary representing the winning slot 
                      (e.g., {'value': '5', 'color': 'red'}).

    Returns:
        The payout amount if the bet wins, and 0 if it loses.
    """
    # bet_details is the dictionary stored in pending_bets
    # e.g., {"user_id": "user1", "type": "number", "value": "10", "amount": 5, ...}
    bet_type = bet_details['type']
    bet_value = bet_details['value']
    winning_value = winning_slot['value']
    winning_color = winning_slot['color']

    if bet_type == 'number':
        if bet_value == winning_value:
            return 35 # Return payout multiplier
    elif bet_type == 'color':
        if bet_value == winning_color:
            return 1 # Return payout multiplier
    elif bet_type == 'even_odd':
        # Any zero ("0", "00", "000", "0000") results in a loss for even/odd bets.
        if '0' in winning_value and all(c == '0' for c in winning_value): # Checks for "0", "00", "000", etc.
            return 0 # Return multiplier 0 for loss
        
        # Only proceed if winning_value is a standard number (1-36)
        try:
            winning_num_int = int(winning_value)
            is_winning_even = winning_num_int % 2 == 0
            if bet_value == 'even' and is_winning_even:
                return 1 # Return multiplier
            elif bet_value == 'odd' and not is_winning_even:
                return 1 # Return multiplier
        except ValueError:
            # This case should ideally not be reached if winning_value is always from the wheel
            # and zeros are handled above.
            return 0 
            
    return 0 # Default to multiplier 0 for no win

def play_round(user_id, table_id):
    """
    Simulates a single round of roulette for a given user at a specific table.
    Manages user balance based on bet and outcome.

    Args:
        user_id (str): The ID of the user playing the round.
        table_id (str): The ID of the table where the game is played.
    """
    table_config = get_table(table_id)
    if not table_config:
        print(f"Error: Table '{table_id}' could not be found. Skipping round.")
        return

    current_round_id = generate_round_id(table_id)
    print(f"\n--- New Round Starting (ID: {current_round_id}) for {user_id} at '{table_config['name']}' (Balance: {get_balance(user_id)}) ---")

    # Simulate betting period: allow user to place multiple bets for the current round
    while True:
        print(f"\nUser {user_id}, you can place a bet for round {current_round_id} or type 'done' for bet type.")
        bet_placed_successfully = place_bet(user_id, table_id, current_round_id)
        if not bet_placed_successfully: # User typed 'done' or failed to place a bet (e.g. insufficient funds)
            # If place_bet returned False because user typed 'done', it's a valid exit.
            # If it returned False due to insufficient funds or other error, that's also handled.
            break 
        
        another_bet = input("Place another bet for this round? (yes/no): ").lower().strip()
        if another_bet != 'yes':
            break
            
    print(f"\n--- Betting phase for round {current_round_id} ended. ---")
    
    # Spin the wheel
    winning_slot = spin_wheel() # spin_wheel uses CURRENT_WHEEL (global wheel config)
    print(f"Wheel is spinning for round {current_round_id}...")
    print(f"The wheel landed on: {winning_slot['value']} ({winning_slot['color']})")

    # Record round result in history
    record_round_result(current_round_id, table_id, winning_slot)

    # Process bets for this round
    bets_for_this_round = get_bets_for_round(current_round_id)
    if not bets_for_this_round:
        print(f"No bets were placed for round {current_round_id}.")
    else:
        print(f"\n--- Processing {len(bets_for_this_round)} bets for round {current_round_id} ---")
        for bet in bets_for_this_round:
            # "Decrypt" bet - for now, just use it directly
            # Note: bet['user_id'] is available if needed to re-verify user, but adjust_balance already handles this
            
            payout_multiplier = check_bet(bet, winning_slot) # check_bet uses global payout logic
            
            if payout_multiplier > 0:
                winnings = payout_multiplier * bet['amount']
                # Balance was already debited at time of bet. Now, credit winnings.
                # The amount to credit is the total payout (winnings + original stake)
                # OR, if the original stake is considered separate, just the profit.
                # Current wallet adjust_balance adds to current. If bet amount was debited,
                # we just add the pure winnings.
                # If payout_multiplier is e.g. 35 (for number), winnings = 35 * amount.
                # User should get back original_bet_amount + (multiplier-1)*original_bet_amount for profit
                # OR total payout = multiplier * original_bet_amount.
                # Since adjust_balance(-amount) was done, we add (multiplier * amount)
                adjust_balance(bet['user_id'], winnings) 
                print(f"User {bet['user_id']}: Bet on {bet['type']} '{bet['value']}' ({bet['amount']}) WON! Payout: {winnings}. Balance: {get_balance(bet['user_id'])}")
            else:
                # Bet amount was already deducted when placed. No further action on loss.
                print(f"User {bet['user_id']}: Bet on {bet['type']} '{bet['value']}' ({bet['amount']}) lost. Balance: {get_balance(bet['user_id'])}")
    
    # Clear pending bets for the processed round
    clear_bets_for_round(current_round_id)
    
    print(f"\n--- Round {current_round_id} for {user_id} at table '{table_config['name']}' ended. ---")
    print(f"{user_id}'s final balance after round: {get_balance(user_id)}")
    print("--- Round End ---\n")
    return current_round_id # Return the ID for potential history viewing

if __name__ == '__main__':
    # --- Admin: Setup Tables ---
    print("--- Admin: Setting up tables ---")
    create_game_table("t1", "Casual Corner", min_bet=5, max_bet=50)
    create_game_table("t2", "High Rollers Den", min_bet=100, max_bet=1000)
    print("--- Table setup complete ---\n")

    # --- User: Setup ---
    player1_id = "player1"
    player2_id = "player2"
    create_user(player1_id, 200)
    create_user(player2_id, 150)

    # --- User: Table Selection (Simplified for demo) ---
    # Let's assume player1 chooses t1, player2 chooses t1 as well for simplicity of demo
    selected_table_id_p1 = "t1"
    selected_table_id_p2 = "t1" # Both players at the same table for one round

    print(f"\n--- {player1_id} joining table ID: {selected_table_id_p1} ---")
    print(f"--- {player2_id} joining table ID: {selected_table_id_p2} ---")

    # --- Gameplay: Simulate one round with multiple players placing bets ---
    # This part is tricky to make fully interactive for multiple users in a linear script.
    # We'll simulate it by calling play_round for one user, which now handles its own betting loop.
    # To show multiple users in one round, play_round would need to be structured differently
    # (e.g., take a list of users, or have a central game loop).
    # For now, we'll run play_round for player1, which will generate a round_id.
    # Then, we'll manually use place_bet for player2 for THE SAME round_id before that round is "spun".
    
    # Player 1 plays a round (which includes their betting phase)
    # We need to capture the round_id generated by player1's play_round call
    # to allow player2 to bet on the same round.
    # This is a bit of a hack for this testing structure. 
    # A real game would have a central loop that manages rounds and betting periods for all users at a table.

    print(f"\n--- {player1_id}'s turn to initiate a round and place bets ---")
    # In a real scenario, a round would be initiated for a table, then users bet.
    # Here, play_round for player1 will generate the round_id.
    
    # Let's refine play_round to just handle one user's interaction for placing bets for a given round_id
    # And have a separate function to "spin and resolve" a round.
    # For now, let's stick to the current structure and show conceptual multi-betting on one round.

    # Generate a round ID for table t1
    active_round_id = generate_round_id(selected_table_id_p1)
    print(f"\n--- New Round ID: {active_round_id} initiated for table {selected_table_id_p1} ---")
    print(f"--- {player1_id} places bets for round {active_round_id} ---")
    place_bet(player1_id, selected_table_id_p1, active_round_id) # P1 places first bet
    place_bet(player1_id, selected_table_id_p1, active_round_id) # P1 places second bet (optional)
    
    print(f"\n--- {player2_id} places bets for the SAME round {active_round_id} ---")
    place_bet(player2_id, selected_table_id_p2, active_round_id) # P2 places a bet

    # Now, "spin" the wheel and process all bets for active_round_id
    print(f"\n--- Spinning wheel and processing bets for round {active_round_id} ---")
    table_config = get_table(selected_table_id_p1) # Assuming t1
    winning_slot = spin_wheel()
    print(f"Wheel landed on: {winning_slot['value']} ({winning_slot['color']}) for round {active_round_id}")
    record_round_result(active_round_id, selected_table_id_p1, winning_slot)

    all_bets_for_round = get_bets_for_round(active_round_id)
    if not all_bets_for_round:
        print(f"No bets were placed for round {active_round_id}.")
    else:
        print(f"\n--- Processing {len(all_bets_for_round)} total bets for round {active_round_id} ---")
        for bet in all_bets_for_round:
            payout_multiplier = check_bet(bet, winning_slot)
            if payout_multiplier > 0:
                winnings = payout_multiplier * bet['amount']
                adjust_balance(bet['user_id'], winnings)
                print(f"User {bet['user_id']}: Bet on {bet['type']} '{bet['value']}' ({bet['amount']}) WON! Payout: {winnings}. Balance: {get_balance(bet['user_id'])}")
            else:
                print(f"User {bet['user_id']}: Bet on {bet['type']} '{bet['value']}' ({bet['amount']}) lost. Balance: {get_balance(bet['user_id'])}")
    
    clear_bets_for_round(active_round_id)
    print(f"--- Round {active_round_id} processing complete. ---")

    # --- User Viewing Past Round Results ---
    print("\n--- View Past Round Results ---")
    while True:
        see_history = input("Do you want to view a past round's result? (yes/no): ").lower().strip()
        if see_history != 'yes':
            break
        round_to_view = input("Enter the Round ID to view (e.g., t1_xxxxxxxx-xxxx-...): ").strip()
        round_data = get_round_info(round_to_view)
        if round_data:
            print(f"Round {round_to_view} Data: {round_data}")
            bets_of_round = get_bets_for_round(round_to_view) # Bets would be cleared, but for demo if not cleared
            if bets_of_round: # This will usually be empty as bets are cleared after processing
                 print(f"  Bets placed for this round (note: usually cleared after processing): {bets_of_round}")
            else:
                 print(f"  (No pending bets found for round {round_to_view} - likely processed and cleared)")
        else:
            print(f"No history found for Round ID: {round_to_view}")

    print("\n--- Final Balances ---")
    print(f"{player1_id}: {get_balance(player1_id)}")
    print(f"{player2_id}: {get_balance(player2_id)}")
