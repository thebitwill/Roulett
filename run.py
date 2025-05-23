# run.py
from webapp import create_app
import os # For later, if we need to ensure DB path is correct relative to app

# Ensure the roulette_game package can be imported
# This might require adjusting PYTHONPATH or ensuring run.py is in the project root
# and roulette_game is a sibling directory. For now, assume direct import works
# or that necessary path adjustments are handled by the execution environment.

# Initialize the database if it doesn't exist
# This should ideally be handled carefully, perhaps only on first run or via a CLI command
from roulette_game.database import initialize_database, DATABASE_NAME
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'roulette_game', DATABASE_NAME)

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}, initializing...")
    # Temporarily change CWD if database.py expects DB in its own dir
    original_cwd = os.getcwd()
    roulette_game_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'roulette_game')
    if not os.path.exists(roulette_game_dir): # Should exist
         os.makedirs(roulette_game_dir, exist_ok=True)
    os.chdir(roulette_game_dir)
    initialize_database() # This will create roulette_game.db inside roulette_game/
    os.chdir(original_cwd)
    print("Database initialized.")
else:
    print(f"Database found at {db_path}.")


app = create_app()

if __name__ == '__main__':
    app.run(debug=True) # Runs on http://127.0.0.1:5000/ by default
