from database import SessionLocal
from routes import get_all_feedback
from models import User

db = SessionLocal()
try:
    current_user = db.query(User).filter(User.username == "vc1").first()
    print("User:", current_user.email, current_user.department_id)
    feedbacks = get_all_feedback(db=db, current_user=current_user)
    print("Feedbacks count:", len(feedbacks))
    # Test if it can be serialized to dict using schemas
    from schemas import FeedbackOutExtended
    for f in feedbacks:
        dto = FeedbackOutExtended.from_orm(f)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
