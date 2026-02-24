from email.message import EmailMessage
import smtplib


def send_feedback_reply(email: str, subject: str, message: str):
    msg = EmailMessage()
    msg.set_content(message)
    msg["Subject"] = subject
    msg["From"] = "feedback@seku.ac.ke"
    msg["To"] = email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("youremail@gmail.com", "your-app-password")
            smtp.send_message(msg)
    except Exception as e:
        print("Failed to send reply:", str(e))
        raise Exception("Could not send reply email")