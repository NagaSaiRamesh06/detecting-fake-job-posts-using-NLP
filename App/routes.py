from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pickle
import cv2
import pytesseract
# Set Tesseract Path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from .database import get_db_connection
from .config import Config
import json
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('main', __name__)
oauth = OAuth()

# Register Clients
# Note: Client ID and Secret are loaded from app.config (Config object) automatically by Authlib
# if named {NAME}_CLIENT_ID and {NAME}_CLIENT_SECRET

# Google
google = oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# GitHub
github = oauth.register(
    name='github',
    api_base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_kwargs={'scope': 'user:email'},
)

# Load Models (Global to the module for performance)
# In a production app, we might lazy load or use a dedicated service.
try:
    tfidf = pickle.load(open(Config.TFIDF_PATH, "rb"))
    model = pickle.load(open(Config.MODEL_PATH, "rb"))
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    tfidf = None
    model = None

@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role'] if user['role'] else 'USER'
            
            # Remember Me
            if request.form.get("remember"):
                session.permanent = True
                # current_app.permanent_session_lifetime handled by config or default (31 days)
            
            # Update Last Login
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = get_db_connection()
            conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (current_time, user['id']))
            conn.commit()
            conn.close()

            # flash('Logged in successfully!', 'success') # Optional: Add nicer notification
            
            # Redirect Admins to Dashboard directly? Or just predict page.
            # user['role'] is reachable via another query or if we selected *
            if user['role'] == 'ADMIN':
                 return redirect(url_for("main.admin"))
            
            return redirect(url_for("main.dashboard"))
        else:
            flash('Invalid username or password', 'error')
            return render_template("login.html")

    return render_template("login.html")

# OAuth Routes
@bp.route('/login/google')
def login_google():
    redirect_uri = url_for('main.auth_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@bp.route('/auth/google')
def auth_google():
    try:
        token = google.authorize_access_token()
        user_info = google.userinfo()
        # user_info contains 'email', 'name', 'picture' etc.
        email = user_info.get('email')
        name = user_info.get('name') or email.split('@')[0]
        
        return handle_oauth_login(email, name)
    except Exception as e:
        flash(f"Google Login Failed: {str(e)}", "error")
        return redirect(url_for("main.login"))

@bp.route('/login/github')
def login_github():
    redirect_uri = url_for('main.auth_github', _external=True)
    return github.authorize_redirect(redirect_uri)

@bp.route('/auth/github')
def auth_github():
    try:
        token = github.authorize_access_token()
        # GitHub API to get user info
        resp = github.get('user', token=token)
        profile = resp.json()
        
        email = profile.get('email')
        # If email is private, we need another call
        if not email:
             resp_emails = github.get('user/emails', token=token)
             emails = resp_emails.json()
             for e in emails:
                 if e.get('primary') and e.get('verified'):
                     email = e.get('email')
                     break
        
        name = profile.get('name') or profile.get('login') or "GitHub User"
        
        if not email:
             flash("Could not retrieve email from GitHub.", "error")
             return redirect(url_for("main.login"))

        return handle_oauth_login(email, name)
    except Exception as e:
         flash(f"GitHub Login Failed: {str(e)}", "error")
         return redirect(url_for("main.login"))

def handle_oauth_login(email, name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (email,))
    user = c.fetchone()
    
    if user:
        # User exists, log them in
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role'] if user['role'] else 'USER'
        
        # Update Last Login
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE users SET last_login = ? WHERE id = ?", (current_time, user['id']))
        conn.commit()
    else:
        # Register new user automatically
        # Since it's OAuth, we can set a random unusable password or separate logic.
        # Here we just set a random hash so they can't login via password unless they reset it.
        import uuid
        random_password = str(uuid.uuid4())
        hashed_password = generate_password_hash(random_password)
        
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'USER')", (email, hashed_password))
        conn.commit()
        
        # Get ID
        c.execute("SELECT * FROM users WHERE username = ?", (email,))
        user = c.fetchone()
        
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = 'USER'
    
    conn.close()
    
    if session.get('role') == 'ADMIN':
        return redirect(url_for("main.admin"))
        
    return redirect(url_for("main.ui_predict"))

@bp.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for("main.login"))

@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        # In a real app, verify email exists and send token.
        # Here we just show success message.
        flash(f"If an account exists for {email}, a reset link has been sent.", "success")
        return redirect(url_for("main.login"))
        
    return render_template("forgot_password.html")

import re

@bp.route("/api/login", methods=["POST"])
def api_login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
         return jsonify({"msg": "Missing username or password"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username") # Validated as Email
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
             flash('Please fill all fields', 'error')
             return render_template("register.html")

        # 1. Check Passwords Match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template("register.html")

        # 2. Validate Email Format (Regex)
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, username):
            flash('Invalid email format', 'error')
            return render_template("register.html")

        # 3. Block Disposable/Fake Domains
        disposable_domains = ["tempmail.com", "mailinator.com", "10minutemail.com", "guerrillamail.com", "yopmail.com", "example.com", "test.com"]
        domain = username.split('@')[-1].lower()
        if domain in disposable_domains:
            flash('Please use an official email address (no disposable emails)', 'error')
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        try:
            fullname = request.form.get("fullname")
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, fullname) VALUES (?, ?, ?)", (username, hashed_password, fullname))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for("main.login"))
        except Exception: 
            flash('Email already registered', 'error')
            return render_template("register.html")

    return render_template("register.html")


from .data_processor import clean_text

# Helper Function for Prediction Logic
def get_prediction(text):
    if not model or not tfidf:
        return {"error": "Model not loaded", "prediction": "Error", "fake_probability": 0}

    # Preprocess Text (Crucial step!)
    cleaned_text = clean_text(text)
    
    if not cleaned_text:
         return {"error": "Invalid input text", "prediction": "Error", "fake_probability": 0}

    vector = tfidf.transform([cleaned_text])
    
    # Check if model supports proba (LinearSVC usually needs probability=True or decision_function)
    # Our AutoML likely picked LinearSVC which might not have predict_proba by default if not set.
    # However, we can use decision_function or CalibratedClassifierCV. 
    # For simplicity, if predict_proba fails, we use predict and fake prob = 0/1 or decision function score.
    
    try:
        probs = model.predict_proba(vector)[0]
        fake_prob = probs[1]
    except AttributeError:
        # Fallback for models without predict_proba (like LinearSVC)
        # Use decision_function and apply sigmoid to get a pseudo-probability
        if hasattr(model, "decision_function"):
            score = model.decision_function(vector)[0]
            import math
            # Sigmoid: 1 / (1 + e^-x)
            # We explicitly handle the sign effectively by the formula
            fake_prob = 1 / (1 + math.exp(-score))
        else:
            prediction = model.predict(vector)[0]
            fake_prob = 1.0 if prediction == 1 else 0.0
    
    # Hybrid Approach (Keywords)
    risk_keywords = ["easy money", "work from home", "no experience", "immediate start", "part time", "students", "weekly pay"]
    keyword_flag = any(k in cleaned_text for k in risk_keywords)

    # If using direct 0/1 prediction from SVM
    if isinstance(fake_prob, float) and fake_prob in [0.0, 1.0]:
         result = "Fake Job" if fake_prob == 1.0 else "Real Job"
         # Adjust threshold logic if we really want keyword influence on hard predictions?
         # For now, trust the model's hard prediction but flag keywords in UI if needed.
         if keyword_flag and result == "Real Job":
             pass # Could force review, but let's stick to model for now.
    else:
        # Probabilistic logic
        threshold = 0.10 if keyword_flag else 0.50 # SVM is calibrated or other models
        result = "Fake Job" if fake_prob > threshold else "Real Job"
    
    # Log Prediction to Database (if user is logged in)
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO predictions (user_id, input_text, prediction_result) VALUES (?, ?, ?)",
                      (session['user_id'], text, result)) # Log full text
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Logging error: {e}")

    return {
        "prediction": result,
        "fake_probability": float(fake_prob)
    }

@bp.route("/ui_predict", methods=["GET", "POST"])
def ui_predict():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    result = ""
    prob = 0
    if request.method == "POST":
        text = request.form.get("description")

        if text and len(text.strip()) > 5:
            pred_data = get_prediction(text)
            if "error" in pred_data:
                result = pred_data["error"]
            else:
                result = pred_data["prediction"]
                prob = pred_data["fake_probability"]
        else:
            result = "Please enter a valid job description (min 5 chars)"
            flash(result, 'warning')

    return render_template("predict.html", result=result, prob=prob)

# Helper: Check if user is admin
def is_admin():
    if 'user_id' not in session:
        return False
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id = ?", (session['user_id'],))
    user = c.fetchone()
    conn.close()
    return user and user['role'] == 'ADMIN'

@bp.route("/admin")
def admin():
    if not is_admin():
        flash("Access Denied: You must be an Admin.", "error")
        return redirect(url_for("main.ui_predict"))

    conn = get_db_connection()
    c = conn.cursor()

    # 1. Fetch Stats
    c.execute("SELECT COUNT(*) FROM users WHERE role != 'ADMIN'")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN'")
    total_admins = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result LIKE 'Fake%'")
    fake_detected = c.fetchone()[0]

    real_detected = total_predictions - fake_detected
    
    fake_rate = 0
    real_rate = 0
    if total_predictions > 0:
        fake_rate = round((fake_detected / total_predictions) * 100, 1)
        real_rate = round((real_detected / total_predictions) * 100, 1)

    # 2. Fetch Users (for Table)
    c.execute("SELECT id, username, role, last_login FROM users ORDER BY id DESC")
    users = c.fetchall()

    # 3. Fetch Recent Predictions
    c.execute("""
        SELECT p.id, u.username, p.input_text, p.prediction_result, p.created_at 
        FROM predictions p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.id DESC LIMIT 20
    """)
    recent_logs = c.fetchall()

    # 4. Fetch Activity Graph Data (Last 30 Days)
    # SQLite DATE() returns YYYY-MM-DD. 
    c.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM predictions 
        GROUP BY date 
        ORDER BY date ASC 
        LIMIT 30
    """)
    activity_data = c.fetchall()
    activity_dates = [row['date'] for row in activity_data]
    activity_counts = [row['count'] for row in activity_data]
    
    conn.close()

    # 5. Load Model Metrics (New JSON)
    model_meta = {}
    try:
        # Check for new metrics file first
        metrics_path = os.path.join(Config.MODEL_DIR, "model_metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                model_meta = json.load(f)
        else:
             # Fallback to old or empty
             with open("Model/model_metadata.json", "r") as f:
                model_meta = json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        # Default structure if file missing
        model_meta = {
            "model_name": "Unknown", 
            "accuracy": 0, 
            "models": {"Logistic Regression": 0, "Naive Bayes": 0, "SVM": 0}
        }

    return render_template("admin.html", 
                         total_users=total_users,
                         total_admins=total_admins,
                         total_predictions=total_predictions,
                         fake_detected=fake_detected,
                         real_detected=real_detected,
                         fake_rate=fake_rate,
                         real_rate=real_rate,
                         users=users,
                         recent_logs=recent_logs,
                         model_meta=model_meta,
                         activity_dates=json.dumps(activity_dates),
                         activity_counts=json.dumps(activity_counts))

@bp.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
        
    # If admin, they might prefer the admin dashboard, but let them see this too if they go to /dashboard directly
    # or redirect them:
    # if session.get('role') == 'ADMIN':
    #     return redirect(url_for('main.admin'))

    conn = get_db_connection()
    c = conn.cursor()
    user_id = session['user_id']

    # 1. Fetch User Stats
    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
    total_scans = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND prediction_result LIKE 'Fake%'", (user_id,))
    fake_found = c.fetchone()[0]
    
    real_found = total_scans - fake_found

    # 2. Fetch User History
    c.execute("""
        SELECT id, input_text, prediction_result, created_at 
        FROM predictions 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT 20
    """, (user_id,))
    history = c.fetchall()
    
    conn.close()

    return render_template("dashboard.html", 
                         total_scans=total_scans,
                         fake_found=fake_found,
                         real_found=real_found,
                         history=history)

@bp.route("/promote/<int:user_id>")
def promote_user(user_id):
    if not is_admin():
        return redirect(url_for("main.login"))
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET role = 'ADMIN' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    flash("User promoted to Admin successfully!", "success")
    return redirect(url_for("main.admin"))

@bp.route("/demote/<int:user_id>")
def demote_user(user_id):
    if not is_admin():
        return redirect(url_for("main.login"))
    
    # Prevent self-demotion (optional but good practice)
    if user_id == session.get('user_id'):
         flash("You cannot demote yourself!", "error")
         return redirect(url_for("main.admin"))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET role = 'USER' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    flash("Admin demoted to User successfully!", "success")
    return redirect(url_for("main.admin"))

    flash("Admin demoted to User successfully!", "success")
    return redirect(url_for("main.admin"))

@bp.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect(url_for("main.login"))
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return redirect(url_for("main.logout"))
        
    return render_template("profile.html", user=user)

@bp.route("/predict", methods=["POST"])
@jwt_required()
def predict_api():
    data = request.get_json()

    if not data or "job_description" not in data:
        return jsonify({"error": "job_description is required"}), 400

    text = data["job_description"]
    pred_data = get_prediction(text)
    
    if "error" in pred_data:
        return jsonify(pred_data), 500
        
    return jsonify(pred_data)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/scan-image", methods=["POST"])
def scan_image():
    print("DEBUG: /scan-image endpoint called") # DEBUG
    # 1. Check if file is present
    if 'file' not in request.files:
        print("DEBUG: No file part in request") # DEBUG
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    # 2. Check if filename is empty
    if file.filename == '':
        print("DEBUG: Empty filename") # DEBUG
        return jsonify({"error": "No file selected"}), 400

    print(f"DEBUG: Processing file: {file.filename}") # DEBUG

    # 3. Validate file type
    if not allowed_file(file.filename):
         print(f"DEBUG: Invalid file extension: {file.filename}") # DEBUG
         return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, webp"}), 400

    if file:
        filename = secure_filename(file.filename)
        
        # Ensure Upload Folder Exists
        if not os.path.exists(Config.UPLOAD_FOLDER):
            try:
                os.makedirs(Config.UPLOAD_FOLDER)
                print(f"DEBUG: Created upload folder: {Config.UPLOAD_FOLDER}") # DEBUG
            except Exception as e:
                print(f"DEBUG: Failed to create upload folder: {e}") # DEBUG
                return jsonify({"error": f"Server Error: Could not create upload directory. {e}"}), 500
            
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        try:
            file.save(filepath)
            print(f"DEBUG: File saved to {filepath}") # DEBUG
        except Exception as e:
             print(f"DEBUG: Failed to save file: {e}") # DEBUG
             return jsonify({"error": f"Server Error: Could not save file. {e}"}), 500

        try:
            # 4. Check for Tesseract
            tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
            print(f"DEBUG: Tesseract Path configured as: {tesseract_cmd}") # DEBUG
            
            if not os.path.exists(tesseract_cmd):
                 print("DEBUG: Tesseract binary not found at path") # DEBUG
                 return jsonify({"error": "Server Configuration Error: Tesseract OCR not found on server."}), 500

            # 5. Process Image
            print("DEBUG: Reading image with OpenCV...") # DEBUG
            img = cv2.imread(filepath)
            if img is None:
                 print("DEBUG: cv2.imread returned None") # DEBUG
                 return jsonify({"error": "Could not read image file. It might be corrupted."}), 400
                 
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            print("DEBUG: Image converted to grayscale") # DEBUG
            
            # Simple thresholding to improve OCR accuracy
            # gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            print("DEBUG: Running pytesseract...") # DEBUG
            text = pytesseract.image_to_string(gray)
            clean_text = text.strip()
            print(f"DEBUG: Extracted text length: {len(clean_text)}") # DEBUG
            
            if not clean_text:
                 print("DEBUG: No text found") # DEBUG
                 return jsonify({"error": "No readable text found in the image."}), 400 # Or 200 with empty text? Better to be explicit.

            # 6. Predict using NLP model
            print("DEBUG: Running NLP prediction...") # DEBUG
            pred_data = get_prediction(clean_text)
            print(f"DEBUG: Prediction result: {pred_data}") # DEBUG
            
            return jsonify({
                "extracted_text": clean_text,
                "prediction": pred_data.get("prediction", "Error"),
                "fake_probability": pred_data.get("fake_probability", 0)
            })

        except Exception as e:
            print(f"ERROR: OCR Exception: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Internal Processing Error: {str(e)}"}), 500
        finally:
            # Cleanup
            if os.path.exists(filepath):
                try:
                   os.remove(filepath)
                   print("DEBUG: Cleanup successful") # DEBUG
                except:
                   pass
