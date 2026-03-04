import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models import Question, QuestionResponse, Feedback

db = SessionLocal()
try:
    questions = db.query(Question).all()
    print(f"Total Questions in DB: {len(questions)}")
    for q in questions:
        print(f"ID: {q.id} | Text: {q.text[:50]}...")
    
    recent_responses = db.query(QuestionResponse).order_by(QuestionResponse.id.desc()).limit(10).all()
    print(f"\nRecent Question Responses:")
    for r in recent_responses:
        print(f"Feedback ID: {r.feedback_id} | Question ID: {r.question_id} | Answer: {r.answer}")

    recent_feedback = db.query(Feedback).order_by(Feedback.id.desc()).limit(5).all()
    print(f"\nRecent Feedback Table Entries:")
    for f in recent_feedback:
        print(f"ID: {f.id} | Rating: {f.rating} | q_4: {f.q_4} | Office: {f.office}")

finally:
    db.close()
