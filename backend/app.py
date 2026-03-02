from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps
import hashlib
from email_service import email_service

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['JWT_EXPIRATION_HOURS'] = 24

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Aaamumo254%",
    database="feedback_portal"
)

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
    
    # Check if first user (becomes admin)
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count_result = cursor.fetchone()
    is_first_user = count_result['count'] == 0
    
    role = 'admin' if is_first_user else data.get('role', 'student')
    
    # Hash password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Insert user
    cursor.execute(
        "INSERT INTO users (fullname, email, password, role) VALUES (%s, %s, %s, %s)",
        (fullname, email, hashed_password, role)
    )
    db.commit()
    
    # Generate token
    token = jwt.encode({
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': token,
        'token_type': 'bearer',
        'email': email,
        'fullname': fullname,
        'role': role
    }), 201

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Hash password for comparison
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Get user
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, hashed_password))
    user = cursor.fetchone()
    
    if not user:
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
    
    name = data.get('name')
    email = data.get('email', user_email)  # Use token email if available
    category = data.get('category', 'Anonymous')
    office = data.get('office', 'general')
    rating = data.get('rating')
    message = data.get('message', '')
    anonymous = data.get('anonymous', 'false')
    
    if not name and not anonymous:
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