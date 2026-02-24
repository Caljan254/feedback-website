import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
from config import Config

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        if not self.username or not self.password:
            print(f"Email not configured. Would send to {to_email}: {subject}")
            print(f"Email body: {body}")
            return True
            
        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        reset_url = f"{Config.FRONTEND_URL}/reset-password.html?token={reset_token}"
        
        subject = "Password Reset Request - Institutional Feedback Portal"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">Password Reset Request</h2>
                <p>You requested to reset your password for the Institutional Feedback Portal.</p>
                <p>Click the link below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    Institutional Feedback Portal Team
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body)
    
    def send_feedback_reply(self, to_email: str, subject: str, message: str, user_name: str = None) -> bool:
        greeting = f"Dear {user_name}," if user_name else "Hello,"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">Response to Your Feedback</h2>
                <p>{greeting}</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
                    {message}
                </div>
                <p>Thank you for your valuable feedback. We appreciate you taking the time to share your thoughts with us.</p>
                <p>Best regards,<br><strong>Institutional Feedback Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body)

def generate_reset_token(length=32):
    """Generate a secure random token for password reset"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

email_service = EmailService()