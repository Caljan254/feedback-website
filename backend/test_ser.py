from database import SessionLocal
from models import Feedback, QuestionResponse
from schemas import FeedbackOutExtended
from sqlalchemy.orm import selectinload
from typing import List

def test_serialization():
    db = SessionLocal()
    try:
        query = db.query(Feedback).options(
            selectinload(Feedback.responses).selectinload(QuestionResponse.question)
        ).filter(Feedback.office == "ict-services")
        
        feedbacks = query.all()
        print(f"Found {len(feedbacks)} feedbacks")
        
        for f in feedbacks:
            try:
                # Test Pydantic serialization
                out = FeedbackOutExtended.from_orm(f)
                print(f"Successfully serialized ID: {f.id}")
            except Exception as e:
                print(f"Failed to serialize ID: {f.id}")
                print(f"Error: {e}")
                
    finally:
        db.close()

if __name__ == "__main__":
    test_serialization()
