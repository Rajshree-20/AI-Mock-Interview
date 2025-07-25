import os
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, jsonify
)
import random
import requests
from database import create_tables, add_user, get_user_by_email, get_all_users

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# FastAPI endpoints
FASTAPI_URL = "http://localhost:8000/upload-resume/"
FASTAPI_FEEDBACK_URL = "http://localhost:8000/submit-answers/"

# Upload config
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create DB tables
create_tables()

# Helper function
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes

@app.route('/')
def home():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not add_user(name, email, password):
            flash('Email already exists. Please log in.', 'error')
            return redirect(url_for('login'))

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)
        if user and user[2] == password:  # user[2] is password
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = get_user_by_email(session['user'])
    if not user:
        return redirect(url_for('logout'))

    raw_users = get_all_users()
    random.shuffle(raw_users)  # just for fun
    leaderboard = [{"name": u[0]} for u in raw_users]

    return render_template(
        'dashboard.html',
        user={'name': user[0], 'email': user[1]},
        leaderboard=leaderboard[:10]
    )

@app.route('/leaderboard')
def leaderboard():
    users = get_all_users()
    leaderboard_data = []

    for user in users:
        leaderboard_data.append({
            'name': user[0],  # user[0] = name
            'score': random.randint(50000, 999999)
        })

    # Sort by score descending
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)

    return {'leaderboard': leaderboard_data}

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route("/interview", methods=["GET", "POST"])
def interview():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        file = request.files.get("resume")
        difficulty = request.form.get("difficulty")

        if not file or not difficulty:
            flash("Please upload a file and select difficulty.", "error")
            return render_template("index.html")

        elif not allowed_file(file.filename):
            flash("Only PDF files are supported.", "error")
            return render_template("index.html")

        try:
            files = {"file": (file.filename, file.stream, file.content_type)}
            data = {"difficulty": difficulty}
            response = requests.post(FASTAPI_URL, files=files, data=data)

            if response.status_code == 200:
                questions = response.json().get("questions", [])
                if not questions:
                    flash("No questions were generated.", "error")
                    return render_template("index.html")
                else:
                    return render_template("interview.html", questions=questions)
            else:
                flash(f"API Error: {response.json().get('message', response.text)}", "error")
                return render_template("index.html")

        except Exception as e:
            flash(f"Request failed: {e}", "error")
            return render_template("index.html")

    return render_template("index.html")

@app.route("/submit-answers", methods=["POST"])
def submit_answers():
    data = request.get_json()
    answers = data.get("answers")
    questions = data.get("questions")

    feedback_data = {
        "questions": questions,
        "answers": answers
    }

    response = requests.post(FASTAPI_FEEDBACK_URL, json=feedback_data)

    if response.status_code == 200:
        feedback = response.json().get("feedback", "No feedback available.")
        return jsonify({"feedback": feedback})
    else:
        return jsonify({"message": "Error generating feedback."}), 500

if __name__ == "__main__":
    app.run(debug=True)
