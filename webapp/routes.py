# webapp/routes.py
from flask import Blueprint, render_template, current_app
import sqlite3 # For testing DB connection from a route

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Example: try to connect to DB and list users to test connection
    # In a real app, DB interactions would be more structured (e.g., via services)
    db_path = current_app.config.get('DATABASE_PATH', 'roulette_game/roulette_game.db') # Fallback for safety
    users_list = []
    error_message = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT username, balance FROM users ORDER BY username LIMIT 5")
        users_rows = cursor.fetchall()
        for row in users_rows:
            users_list.append({"username": row["username"], "balance": row["balance"]})
        conn.close()
    except Exception as e:
        error_message = str(e)
        print(f"Error connecting to DB or fetching users in index route: {e}")

    return render_template('index.html', title='Welcome', users=users_list, db_error=error_message)

@main_bp.route('/hello')
def hello():
    return "Hello, World from Roulette App!"
