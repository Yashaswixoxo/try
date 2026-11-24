from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import sqlite3
from functools import wraps
import json
import random
import string
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import ML model functions
from model import predict_food, get_calorie_estimate

# Import database functions
from database import (
    init_db, add_user, verify_user, log_calorie_entry,
    get_user_data, calculate_bmi_data,
    create_pending_signup, get_pending_signup,
    complete_pending_signup, user_has_paid
)

# Initialize database
init_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'All fields required'}), 400
    
    # Save as PENDING — user does not exist until payment succeeds
    success, message, token = create_pending_signup(username, email, password)
    if success:
        return jsonify({
            'message': 'Account created. Please complete payment.',
            'redirect': url_for('pay', token=token)
        }), 201
    return jsonify({'error': message}), 400


@app.route('/pay')
def pay():
    """Simulated payment page."""
    token = request.args.get('token')
    pending = get_pending_signup(token)
    if not pending:
        return redirect(url_for('index'))
    if pending.get('paid') == 1:
        return redirect(url_for('payment_success', txn_id=pending.get('txn_id')))
    return render_template('pay.html',
                           email=pending['email'],
                           username=pending['username'],
                           amount=999,
                           token=token)


@app.route('/pay', methods=['POST'])
def process_payment():
    """SIMULATED gateway — no real money moves."""
    data = request.json
    token = data.get('token')
    if not token:
        return jsonify({'error': 'Missing token'}), 400
    pending = get_pending_signup(token)
    if not pending:
        return jsonify({'error': 'Invalid payment session'}), 400
    
    time.sleep(1.5)  # fake gateway latency
    
    date_str = datetime.now().strftime("%Y%m%d")
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    txn_id = f"TXN-{date_str}-{rand_str}"
    
    success, message = complete_pending_signup(token, txn_id)
    if success:
        return jsonify({
            'status': 'success',
            'txn_id': txn_id,
            'amount': 999,
            'currency': 'NPR',
            'redirect': url_for('payment_success', txn_id=txn_id)
        }), 200
    return jsonify({'error': message}), 400


@app.route('/payment-success')
def payment_success():
    txn_id = request.args.get('txn_id', 'N/A')
    return render_template('payment_success.html', txn_id=txn_id, amount=999)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = verify_user(email, password)
    if user:
        # Block logins that haven't paid
        if not user_has_paid(email):
            return jsonify({
                'error': 'Membership payment required. Please complete signup.'
            }), 402
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Login successful', 'username': user['username']}), 200
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/detect-calorie', methods=['POST'])
def detect_calorie():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    weight = request.form.get('weight', 100)
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        weight = float(weight)
    except:
        weight = 100
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    food_name, confidence = predict_food(filepath)
    calories = get_calorie_estimate(food_name, weight)
    
    os.remove(filepath)
    
    result = {
        'food_name': food_name,
        'confidence': round(confidence * 100, 2),
        'calories': round(calories, 2),
        'weight': weight
    }
    
    if 'user_id' in session:
        log_calorie_entry(session['user_id'], food_name, calories, weight)
    
    return jsonify(result), 200


@app.route('/bmi-calculator', methods=['POST'])
@login_required
def bmi_calculator():
    data = request.json
    height = data.get('height')
    weight = data.get('weight')
    
    if not height or not weight:
        return jsonify({'error': 'Height and weight required'}), 400
    
    try:
        height = float(height) / 100
        weight = float(weight)
        bmi = weight / (height ** 2)
        
        if bmi < 18.5:
            category = 'Underweight'
        elif bmi < 25:
            category = 'Normal'
        elif bmi < 30:
            category = 'Overweight'
        else:
            category = 'Obese'
        
        calculate_bmi_data(session['user_id'], height * 100, weight, bmi, category)
        
        return jsonify({
            'bmi': round(bmi, 2),
            'category': category
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/analytics/<period>')
@login_required
def analytics(period):
    valid_periods = ['daily', 'weekly', 'monthly', 'annual']
    if period not in valid_periods:
        return jsonify({'error': 'Invalid period'}), 400
    
    data = get_user_data(session['user_id'], period)
    return jsonify(data), 200


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)