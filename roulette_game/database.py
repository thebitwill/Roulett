# roulette_game/database.py
import sqlite3
import os
import datetime

DATABASE_NAME = "roulette_game.db"

def get_db_connection():
    """Creates and returns a database connection object."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;") # Enable foreign key support
    return conn

def initialize_database():
    """
    Initializes the SQLite database by creating tables if they don't already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL statements for creating tables
    # Using TEXT for IDs to allow for UUIDs or other string-based identifiers later.
    # Using REAL for currency.
    # Using BLOB for encrypted data.
    # Using TEXT for timestamps, to be stored in ISO8601 format.

    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        balance REAL NOT NULL DEFAULT 0
    );
    """

    create_casino_wallets_table = """
    CREATE TABLE IF NOT EXISTS casino_wallets (
        wallet_id TEXT PRIMARY KEY,
        balance REAL NOT NULL DEFAULT 0
    );
    """

    create_game_tables_table = """
    CREATE TABLE IF NOT EXISTS game_tables (
        table_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        min_bet REAL NOT NULL DEFAULT 0,
        max_bet REAL NOT NULL DEFAULT 1000
    );
    """

    create_rounds_table = """
    CREATE TABLE IF NOT EXISTS rounds (
        round_id TEXT PRIMARY KEY,
        table_id TEXT NOT NULL,
        winning_slot_value TEXT,
        winning_slot_color TEXT,
        timestamp_start TEXT NOT NULL,
        timestamp_end TEXT,
        FOREIGN KEY (table_id) REFERENCES game_tables (table_id)
    );
    """

    create_bets_table = """
    CREATE TABLE IF NOT EXISTS bets (
        bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        encrypted_payload BLOB NOT NULL,
        timestamp_placed TEXT NOT NULL,
        FOREIGN KEY (round_id) REFERENCES rounds (round_id),
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """

    try:
        cursor.executescript(f"""
            BEGIN;
            {create_users_table}
            {create_casino_wallets_table}
            {create_game_tables_table}
            {create_rounds_table}
            {create_bets_table}
            COMMIT;
        """)
        print("Database initialized: Tables created or already exist.")
        
        # Optionally, add a default casino wallet if it doesn't exist
        cursor.execute("SELECT * FROM casino_wallets WHERE wallet_id = 'main_casino_wallet'")
        if not cursor.fetchone():
            main_wallet_id = "main_casino_wallet"
            initial_casino_balance = 1000000.0 # Standard large amount for casino
            cursor.execute("INSERT INTO casino_wallets (wallet_id, balance) VALUES (?, ?)", 
                           (main_wallet_id, initial_casino_balance))
            conn.commit()
            print(f"Default casino wallet '{main_wallet_id}' created with balance {initial_casino_balance}.")

    except sqlite3.Error as e:
        print(f"An error occurred during database initialization: {e}")
        conn.rollback() # Rollback changes if any error occurs
    finally:
        conn.close()

if __name__ == '__main__':
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
    if os.path.exists(db_path):
        print(f"Database file '{db_path}' already exists. Running initialize_database() again is safe.")
    else:
        print(f"Database file '{db_path}' does not exist. It will be created.")
        
    initialize_database()
    
    print("\n--- Verifying Database Schema and Initial Data ---")
    conn_verify = get_db_connection()
    cursor_verify = conn_verify.cursor()
    
    print("\nTables:")
    cursor_verify.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor_verify.fetchall()
    for table in tables:
        print(f"- {table[0]}")
        cursor_verify.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor_verify.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] else ''}")

    print("\nCasino Wallets:")
    cursor_verify.execute("SELECT * FROM casino_wallets;")
    wallets = cursor_verify.fetchall()
    if wallets:
        for wallet in wallets:
            print(f"- ID: {wallet[0]}, Balance: {wallet[1]}")
    else:
        print("No casino wallets found (this might be an issue if initialization failed to add one).")
        
    conn_verify.close()
    print("\n--- Database Script Demonstration Complete ---")
