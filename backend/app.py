from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import bcrypt
from config import Config
from email_service import email_service
import re

app = Flask(__name__)
CORS(app)

# Simple HTML sanitizer to prevent XSS
def sanitize_html(text: str) -> str:
    if not text:
        return text
    # Strip script tags and other dangerous elements
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<.*?>', '', text) # Remove all HTML tags for safety
    return text.strip()

# Configuration
app.config['SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_EXPIRATION_HOURS'] = 24

# Security Headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data:; connect-src 'self';"
    return response

# Standardized DB Connection helper
def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=int(Config.DB_PORT)
    )

db = get_db_connection()
cursor = db.cursor(dictionary=True)

# Ensure database has required columns
def ensure_database_schema():
    """Check if the feedback table has the required status columns"""
    try:
        cursor.execute("SHOW COLUMNS FROM feedback LIKE 'is_read'")
        if not cursor.fetchone():
            print("Adding missing columns to feedback table...")
            cursor.execute("""
                ALTER TABLE feedback 
                ADD COLUMN is_read BOOLEAN DEFAULT FALSE,
                ADD COLUMN read_at DATETIME DEFAULT NULL,
                ADD COLUMN replied_at DATETIME DEFAULT NULL,
                ADD COLUMN reply_message TEXT DEFAULT NULL
            """)
            db.commit()
            print("Database schema updated successfully")
    except Exception as e:
        print(f"Error checking database schema: {e}")

# Call schema check
ensure_database_schema()

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_email = data['email']
            
            # Get user from database
            cursor.execute("SELECT * FROM users WHERE email = %s", (current_user_email,))
            current_user = cursor.fetchone()
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

# Home route
@app.route("/")
def home():
    return jsonify({
        "message": "Feedback Portal API",
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login",
            "submit_feedback": "POST /submit-feedback",
            "user_feedback": "GET /user/feedback (requires token)",
            "admin_feedback": "GET /admin/feedback (requires admin token)",
            "mark_read": "POST /admin/feedback/<id>/read (requires admin token)",
            "mark_answered": "POST /admin/feedback/<id>/answered (requires admin token)",
            "send_reply": "POST /send-reply (requires admin token)"
        }
    })

# Register user
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    fullname = data.get('fullname', email.split('@')[0])
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Prevent unauthorized admin registration
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count_result = cursor.fetchone()
    is_first_user = count_result['count'] == 0
    
    assigned_role = data.get('role', 'student')
    if not is_first_user:
        if assigned_role == 'admin':
            # Deny admin role in public registration
            assigned_role = 'student'
    else:
        assigned_role = 'admin'
    
    # Hash password with bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    # Insert user - using 'hashed_password' column name from models.py
    cursor.execute(
        "INSERT INTO users (fullname, email, hashed_password, role) VALUES (%s, %s, %s, %s)",
        (fullname, email, hashed_password, assigned_role)
    )
    db.commit()
    
    # Generate token
    token = jwt.encode({
        'email': email,
        'role': assigned_role,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': token,
        'token_type': 'bearer',
        'email': email,
        'fullname': fullname,
        'role': assigned_role
    }), 201

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Get user
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = jwt.encode({
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'access_token': token,
        'token_type': 'bearer',
        'email': user['email'],
        'fullname': user['fullname'],
        'role': user['role']
    })

# Submit feedback (works with or without token)
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Check if user is authenticated via token
    auth_header = request.headers.get('Authorization')
    user_email = None
    
    if auth_header and auth_header.startswith('Bearer '):
        try:
            token = auth_header.split(' ')[1]
            token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_email = token_data['email']
        except:
            pass
    
    name = sanitize_html(data.get('name'))
    email = data.get('email', user_email)  # Use token email if available
    category = sanitize_html(data.get('category', 'Anonymous'))
    office = sanitize_html(data.get('office', 'general'))
    rating = sanitize_html(data.get('rating'))
    message = sanitize_html(data.get('message', ''))
    anonymous = data.get('anonymous', 'false')
    
    if not name and not anonymous == 'true':
        name = 'Anonymous'
    
    # Insert feedback with status fields
    cursor.execute("""
        INSERT INTO feedback (
            name, email, category, office, rating, message, anonymous, created_at,
            is_read, read_at, replied_at, reply_message
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        name, email, category, office, rating, message, anonymous, datetime.now(),
        False, None, None, None  # Default values for status fields
    ))
    db.commit()
    
    feedback_id = cursor.lastrowid

    # Send notification to admins
    try:
        cursor.execute("SELECT fullname, email FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()
        for admin in admins:
            if admin['email']:
                email_service.send_new_feedback_notification(
                    to_email=admin['email'],
                    department_name=office,
                    feedback_data={
                        "name": name,
                        "email": email,
                        "rating": rating,
                        "message": message,
                        "tracking_id": f"ID-{feedback_id}"
                    }
                )
    except Exception as e:
        print(f"Error sending notifications in app.py: {e}")
    
    return jsonify({
        'id': feedback_id,
        'message': 'Feedback submitted successfully',
        'status': 'success'
    }), 201

# Get user's own feedback
@app.route("/user/feedback", methods=["GET"])
@token_required
def get_user_feedback(current_user):
    """
    Get feedback for the currently logged-in user only
    """
    user_email = current_user['email']
    
    cursor.execute("""
        SELECT id, name, email, category, office, rating, message, anonymous, 
               created_at, is_read, read_at, replied_at, reply_message
        FROM feedback 
        WHERE email = %s 
        ORDER BY created_at DESC
    """, (user_email,))
    
    feedback = cursor.fetchall()
    
    # Format dates for JSON
    for item in feedback:
        if item.get('created_at'):
            item['created_at'] = item['created_at'].isoformat() if hasattr(item['created_at'], 'isoformat') else str(item['created_at'])
        if item.get('read_at'):
            item['read_at'] = item['read_at'].isoformat() if hasattr(item['read_at'], 'isoformat') else str(item['read_at'])
        if item.get('replied_at'):
            item['replied_at'] = item['replied_at'].isoformat() if hasattr(item['replied_at'], 'isoformat') else str(item['replied_at'])
    
    return jsonify(feedback)

# Admin: Get all feedback
@app.route("/admin/feedback", methods=["GET"])
@token_required
def get_all_feedback(current_user):
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Forbidden - Admins only'}), 403
    
    cursor.execute("""
        SELECT id, name, email, category, office, rating, message, anonymous, 
               created_at, is_read, read_at, replied_at, reply_message
        FROM feedback 
        ORDER BY created_at DESC
    """)
    feedback = cursor.fetchall()
    
    # Format dates
    for item in feedback:
        if item.get('created_at'):
            item['created_at'] = item['created_at'].isoformat() if hasattr(item['created_at'], 'isoformat') else str(item['created_at'])
        if item.get('read_at'):
            item['read_at'] = item['read_at'].isoformat() if hasattr(item['read_at'], 'isoformat') else str(item['read_at'])
        if item.get('replied_at'):
            item['replied_at'] = item['replied_at'].isoformat() if hasattr(item['replied_at'], 'isoformat') else str(item['replied_at'])
    
    return jsonify(feedback)

# Mark feedback as read
@app.route("/admin/feedback/<int:feedback_id>/read", methods=["POST"])
@token_required
def mark_feedback_read(current_user, feedback_id):
    """Mark feedback as read when admin views it"""
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Forbidden - Admins only'}), 403
    
    try:
        cursor.execute("""
            UPDATE feedback 
            SET is_read = TRUE, read_at = NOW() 
            WHERE id = %s
        """, (feedback_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Feedback not found'}), 404
            
        return jsonify({'message': 'Feedback marked as read'}), 200
    except Exception as e:
        print(f"Error marking as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Mark feedback as answered
@app.route("/admin/feedback/<int:feedback_id>/answered", methods=["POST"])
@token_required
def mark_feedback_answered(current_user, feedback_id):
    """Mark feedback as answered when admin replies"""
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Forbidden - Admins only'}), 403
    
    try:
        cursor.execute("""
            UPDATE feedback 
            SET replied_at = NOW() 
            WHERE id = %s
        """, (feedback_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Feedback not found'}), 404
            
        return jsonify({'message': 'Feedback marked as answered'}), 200
    except Exception as e:
        print(f"Error marking as answered: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Send reply and mark as answered
@app.route("/send-reply", methods=["POST"])
@token_required
def send_reply(current_user):
    """Send reply to user and mark feedback as answered"""
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Forbidden - Admins only'}), 403
    
    data = request.get_json()
    
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')
    feedback_id = data.get('feedback_id')
    
    if not email or not subject or not message or not feedback_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Update feedback with reply info - mark as both read and answered
        cursor.execute("""
            UPDATE feedback 
            SET replied_at = NOW(), 
                reply_message = %s,
                is_read = TRUE,
                read_at = NOW()
            WHERE id = %s
        """, (message, feedback_id))
        db.commit()
        
        # Send actual email using email_service
        try:
            # Try to get the user's name from the feedback record
            cursor.execute("SELECT name FROM feedback WHERE id = %s", (feedback_id,))
            fb_record = cursor.fetchone()
            user_name = fb_record['name'] if fb_record and fb_record.get('name') else None
            
            email_sent = email_service.send_feedback_reply(
                to_email=email,
                subject=subject or "Response to your feedback",
                message=message,
                user_name=user_name
            )
            if email_sent:
                print(f"Email sent successfully to {email}")
            else:
                print(f"Failed to send email to {email}")
        except Exception as email_err:
            print(f"Error sending email: {str(email_err)}")
        
        return jsonify({'message': 'Reply sent successfully and marked as answered'}), 200
    except Exception as e:
        print(f"Error sending reply: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Get current user profile
@app.route("/user/me", methods=["GET"])
@token_required
def get_user_profile(current_user):
    return jsonify({
        'id': current_user['id'],
        'fullname': current_user['fullname'],
        'email': current_user['email'],
        'role': current_user['role']
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)