import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models import Question

def populate_standard_questions():
    db = SessionLocal()
    try:
        # Standard IDs used in generated forms
        standards = [
            (3, "What was the primary purpose of your visit?"),
            (5, "How would you rate the quality of service/instruction?"),
            (7, "Rating of facility aspect 1"),
            (9, "Rating of facility aspect 2"),
            (11, "Rating of facility aspect 3"),
            (15, "Rate your experience with communication/professionalism"),
            (17, "How easy was it to access the service/office?"),
            (23, "Overall, how would you rate your experience with this office?")
        ]
        
        for qid, text in standards:
            existing = db.query(Question).filter(Question.id == qid).first()
            if not existing:
                print(f"Adding Standard Question ID {qid}...")
                new_q = Question(id=qid, text=text, options="Excellent,Good,Average,Poor,Not Applicable")
                db.add(new_q)
            else:
                print(f"Question ID {qid} already exists.")
        
        db.commit()
        print("Standard questions populated successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_standard_questions()
