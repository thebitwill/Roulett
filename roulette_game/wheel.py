import random

# Maximum number of zeros allowed
MAX_ZEROS = 4

def generate_wheel(num_zeros=1):
    """
    Generates a roulette wheel configuration based on the number of zeros.

    Args:
        num_zeros (int): The number of zero slots to include (1 to MAX_ZEROS).
                         Default is 1 (standard European wheel).

    Returns:
        A list of dictionaries, where each dictionary represents a slot
        with 'value' and 'color'. Returns None if num_zeros is invalid.
    """
    if not 1 <= num_zeros <= MAX_ZEROS:
        print(f"Error: Number of zeros must be between 1 and {MAX_ZEROS}.")
        return None

    wheel = []
    # Add zero slots
    for i in range(num_zeros):
        if i == 0:
            wheel.append({"value": "0", "color": "green"})
        else:
            wheel.append({"value": "0" * (i + 1), "color": "green"}) # 0, 00, 000, ...

    # Standard numbers 1-36
    numbers = [
        {"value": "1", "color": "red"}, {"value": "2", "color": "black"},
        {"value": "3", "color": "red"}, {"value": "4", "color": "black"},
        {"value": "5", "color": "red"}, {"value": "6", "color": "black"},
        {"value": "7", "color": "red"}, {"value": "8", "color": "black"},
        {"value": "9", "color": "red"}, {"value": "10", "color": "black"},
        {"value": "11", "color": "black"}, {"value": "12", "color": "red"},
        {"value": "13", "color": "black"}, {"value": "14", "color": "red"},
        {"value": "15", "color": "black"}, {"value": "16", "color": "red"},
        {"value": "17", "color": "black"}, {"value": "18", "color": "red"},
        {"value": "19", "color": "red"}, {"value": "20", "color": "black"},
        {"value": "21", "color": "red"}, {"value": "22", "color": "black"},
        {"value": "23", "color": "red"}, {"value": "24", "color": "black"},
        {"value": "25", "color": "red"}, {"value": "26", "color": "black"},
        {"value": "27", "color": "red"}, {"value": "28", "color": "black"},
        {"value": "29", "color": "black"}, {"value": "30", "color": "red"},
        {"value": "31", "color": "black"}, {"value": "32", "color": "red"},
        {"value": "33", "color": "black"}, {"value": "34", "color": "red"},
        {"value": "35", "color": "black"}, {"value": "36", "color": "red"}
    ]
    wheel.extend(numbers)
    return wheel

# Global variable to hold the active wheel configuration
CURRENT_WHEEL = generate_wheel() # Default to European wheel (1 zero)

def set_number_of_zeros(num):
    """
    Updates the global CURRENT_WHEEL configuration.

    Args:
        num (int): The desired number of zeros for the wheel.
    """
    global CURRENT_WHEEL
    new_wheel = generate_wheel(num)
    if new_wheel:
        CURRENT_WHEEL = new_wheel
        print(f"\nSuccessfully updated wheel to have {num} zero(s).")
    else:
        print(f"Failed to update wheel. Using previous configuration.")

def spin_wheel():
  """
  Simulates spinning the currently configured roulette wheel.

  Returns:
    A dictionary representing the selected slot from CURRENT_WHEEL,
    containing its 'value' and 'color'.
    Returns None if CURRENT_WHEEL is not set (should not happen with default).
  """
  if not CURRENT_WHEEL:
        print("Error: Wheel is not configured.")
        return None
  return random.choice(CURRENT_WHEEL)

if __name__ == '__main__':
  # Example usage:
  print("--- Default Wheel (1 Zero) ---")
  if CURRENT_WHEEL:
      for slot in CURRENT_WHEEL:
          print(slot, end=" ")
      print("\nSpinning default wheel...")
      for _ in range(3):
          selected_slot = spin_wheel()
          if selected_slot:
              print(f"Landed on: {selected_slot['value']} ({selected_slot['color']})")

  print("\n--- Configuring Wheel to 2 Zeros ---")
  set_number_of_zeros(2)
  if CURRENT_WHEEL:
      for slot in CURRENT_WHEEL:
          print(slot, end=" ")
      print("\nSpinning 2-zero wheel...")
      for _ in range(3):
          selected_slot = spin_wheel()
          if selected_slot:
              print(f"Landed on: {selected_slot['value']} ({selected_slot['color']})")

  print("\n--- Configuring Wheel to 4 Zeros ---")
  set_number_of_zeros(4)
  if CURRENT_WHEEL:
      for slot in CURRENT_WHEEL:
          print(slot, end=" ")
      print("\nSpinning 4-zero wheel...")
      for _ in range(3):
          selected_slot = spin_wheel()
          if selected_slot:
            print(f"Landed on: {selected_slot['value']} ({selected_slot['color']})")
  
  print("\n--- Attempting to Configure Wheel to 5 Zeros (invalid) ---")
  set_number_of_zeros(5) # This should show an error and keep the 4-zero wheel
  if CURRENT_WHEEL:
      print("Current wheel configuration (should remain 4 zeros):")
      for slot in CURRENT_WHEEL:
          print(slot, end=" ")
      print("\nSpinning current wheel...")
      selected_slot = spin_wheel()
      if selected_slot:
          print(f"Landed on: {selected_slot['value']} ({selected_slot['color']})")
