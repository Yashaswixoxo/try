from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import sqlite3
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import ML model functions
from model import predict_food, get_calorie_estimate

# Import database functions
from database import init_db, add_user, verify_user, log_calorie_entry, get_user_data, calculate_bmi_data

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
    
    success, message = add_user(username, email, password)
    if success:
        return jsonify({'message': 'Account created successfully'}), 201
    return jsonify({'error': message}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = verify_user(email, password)
    if user:
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
    weight = request.form.get('weight', 100)  # Default 100g
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        weight = float(weight)
    except:
        weight = 100
    
    # Save file temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Predict food and calories
    food_name, confidence = predict_food(filepath)
    calories = get_calorie_estimate(food_name, weight)
    
    # Clean up
    os.remove(filepath)
    
    result = {
        'food_name': food_name,
        'confidence': round(confidence * 100, 2),
        'calories': round(calories, 2),
        'weight': weight
    }
    
    # If logged in, save to database
    if 'user_id' in session:
        log_calorie_entry(session['user_id'], food_name, calories, weight)
    
    return jsonify(result), 200

@app.route('/bmi-calculator', methods=['POST'])
@login_required
def bmi_calculator():
    data = request.json
    height = data.get('height')  # in cm
    weight = data.get('weight')  # in kg
    
    if not height or not weight:
        return jsonify({'error': 'Height and weight required'}), 400
    
    try:
        height = float(height) / 100  # Convert to meters
        weight = float(weight)
        bmi = weight / (height ** 2)
        
        # Determine category
        if bmi < 18.5:
            category = 'Underweight'
        elif bmi < 25:
            category = 'Normal'
        elif bmi < 30:
            category = 'Overweight'
        else:
            category = 'Obese'
        
        # Save to database
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
    """Get calorie analytics for daily, weekly, monthly, or annual periods"""
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
    app.run(debug=True, host='0.0.0.0', port=5000)