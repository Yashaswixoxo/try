import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import secrets

DATABASE = 'calorie_tracker.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Calorie entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calorie_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            calories REAL NOT NULL,
            weight REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # BMI records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Pending signups (membership payment flow)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            paid INTEGER DEFAULT 0,
            txn_id TEXT,
            paid_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, email, password):
    """Add a new user to the database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    except Exception as e:
        return False, str(e)

def verify_user(email, password):
    """Verify user credentials"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        }
    return None

def log_calorie_entry(user_id, food_name, calories, weight):
    """Log a calorie entry for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO calorie_entries (user_id, food_name, calories, weight) VALUES (?, ?, ?, ?)',
        (user_id, food_name, calories, weight)
    )
    conn.commit()
    conn.close()

def calculate_bmi_data(user_id, height, weight, bmi, category):
    """Save BMI calculation"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO bmi_records (user_id, height, weight, bmi, category) VALUES (?, ?, ?, ?, ?)',
        (user_id, height, weight, bmi, category)
    )
    conn.commit()
    conn.close()

def get_user_data(user_id, period):
    """Get user's calorie data for specified period"""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.now()
    
    if period == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'weekly':
        start_date = now - timedelta(days=7)
    elif period == 'monthly':
        start_date = now - timedelta(days=30)
    elif period == 'annual':
        start_date = now - timedelta(days=365)
    
    cursor.execute('''
        SELECT food_name, calories, weight, timestamp 
        FROM calorie_entries 
        WHERE user_id = ? AND timestamp >= ?
        ORDER BY timestamp DESC
    ''', (user_id, start_date))
    
    entries = cursor.fetchall()
    
    cursor.execute('''
        SELECT height, weight, bmi, category, timestamp 
        FROM bmi_records 
        WHERE user_id = ? AND timestamp >= ?
        ORDER BY timestamp DESC
    ''', (user_id, start_date))
    
    bmi_records = cursor.fetchall()
    
    conn.close()
    
    total_calories = sum([entry['calories'] for entry in entries])
    avg_calories = total_calories / len(entries) if entries else 0
    
    daily_data = {}
    for entry in entries:
        date = entry['timestamp'].split()[0]
        if date not in daily_data:
            daily_data[date] = 0
        daily_data[date] += entry['calories']
    
    food_counts = {}
    for entry in entries:
        food = entry['food_name']
        food_counts[food] = food_counts.get(food, 0) + 1
    
    return {
        'period': period,
        'total_entries': len(entries),
        'total_calories': round(total_calories, 2),
        'average_calories': round(avg_calories, 2),
        'daily_breakdown': daily_data,
        'food_frequency': food_counts,
        'recent_entries': [dict(entry) for entry in entries[:10]],
        'bmi_records': [dict(record) for record in bmi_records],
        'latest_bmi': dict(bmi_records[0]) if bmi_records else None
    }


# ============================================================
# SIMULATED MEMBERSHIP PAYMENT SYSTEM
# ============================================================

def create_pending_signup(username, email, password):
    """Save a pending signup (NOT a real user yet). Returns (success, message, token)."""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered", None

        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already taken", None

        token = secrets.token_urlsafe(24)
        password_hash = generate_password_hash(password)

        cursor.execute('DELETE FROM pending_signups WHERE email = ?', (email,))
        cursor.execute(
            '''INSERT INTO pending_signups 
               (token, username, email, password_hash) 
               VALUES (?, ?, ?, ?)''',
            (token, username, email, password_hash)
        )
        conn.commit()
        conn.close()
        return True, "Pending signup created", token
    except Exception as e:
        return False, str(e), None


def get_pending_signup(token):
    """Fetch a pending signup by token."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pending_signups WHERE token = ?', (token,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def complete_pending_signup(token, txn_id):
    """Move pending -> real user with a paid record. Returns (success, message)."""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM pending_signups WHERE token = ?', (token,))
        pending = cursor.fetchone()
        if not pending:
            conn.close()
            return False, "Invalid payment token"

        if pending['paid'] == 1:
            conn.close()
            return False, "Payment already processed"

        cursor.execute(
            '''INSERT INTO users (username, email, password_hash) 
               VALUES (?, ?, ?)''',
            (pending['username'], pending['email'], pending['password_hash'])
        )

        cursor.execute(
            '''UPDATE pending_signups 
               SET paid = 1, txn_id = ?, paid_at = CURRENT_TIMESTAMP 
               WHERE token = ?''',
            (txn_id, token)
        )
        conn.commit()
        conn.close()
        return True, "Membership activated"
    except sqlite3.IntegrityError as e:
        return False, f"Account creation failed: {e}"
    except Exception as e:
        return False, str(e)


def user_has_paid(email):
    """Check if user's email has a completed payment record."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT 1 FROM pending_signups WHERE email = ? AND paid = 1 LIMIT 1',
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None