🥗 Smart Calorie Tracker

An AI web app that identifies food from photos and tracks nutrition using deep learning.

Core Features
Instant Food Detection: Upload photo → AI identifies food
Calorie Calculation: Enter weight → Get accurate calories
User Dashboard: Track history, BMI, and analytics
Dual Access: Guest (quick check) or Registered (full tracking)

🛠 Tech Stack
Layer Technologies
Backend Python 3.8+, Flask
ML TensorFlow, InceptionV3
Frontend HTML5, CSS3, JavaScript, Chart.js
Database SQLite
Security PBKDF2-SHA256
ML Model: Transfer Learning with InceptionV3

What We Did:
Used InceptionV3 pre-trained on ImageNet (1.4M images)
Fine-tuned on 20 food classes from Food-101 dataset
Trained in Google Colab on GPU
Saved as food_classifier_final.h5
Specs:

Input: 299×299 pixel images
Output: 20 food classes with confidence scores
Accuracy: 85-95% on trained classes
The 20 Foods:
apple_pie, baklava, beef_tartare, bread_pudding, cheese_plate,
chicken_quesadilla, churros, creme_brulee, edamame, filet_mignon,
fish_and_chips, foie_gras, fried_rice, grilled_salmon, onion_rings,
pad_thai, panna_cotta, samosa, scallops, sushi

Key Algorithms

1. Food Recognition (CNN)

Image → Preprocess (299×299) → InceptionV3 → Softmax → Food Class 2. Calorie Calculation 3. BMI Calculation 4. Authentication
Password + Salt → PBKDF2 (260,000 iterations) → Secure Hash

To Start

bash

# 1. Clone & setup

git clone <url>
cd smart-calorie-tracker
python -m venv venv
source venv/bin/activate # Mac/Linux

# 2. Install

pip install -r requirements.txt

# 3. Run

python app.py

# Visit http://localhost:5000

📁 Project Structure
smart-calorie-tracker/
├── app.py # Main Flask app
├── model.py # ML model & predictions
├── database.py # Database operations
├── requirements.txt # Dependencies
├── templates/ # HTML pages
├── static/ # CSS, JS files
└── uploads/ # Temp image storage

📈 Performance

Algorithm Speed Accuracy
Food Recognition ~50ms 85-95%
Calorie Calculation <1ms ±10%
BMI Calculation <1ms 100%
Database Queries O(log n) 100%

🎯 Future Improvements

Add more food classes (40+)
Automatic portion estimation
Barcode scanning
Mobile app
Export reports (PDF/CSV)
