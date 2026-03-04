
import sqlalchemy
from database import SessionLocal
from models import Feedback

def check_promises():
    db = SessionLocal()
    try:
        feedback = db.query(Feedback).all()
        found = False
        for f in feedback:
            for attr in ['rating', 'q_0', 'q_1', 'q_2', 'q_3', 'q_4']:
                val = getattr(f, attr)
                if val == '[object Promise]':
                    print(f"Found [object Promise] in feedback ID {f.id}, column {attr}")
                    setattr(f, attr, 'N/A')
                    found = True
        if found:
            db.commit()
            print("Fixed entries.")
        else:
            print("No entries with [object Promise] found.")
    finally:
        db.close()

if __name__ == "__main__":
    check_promises()
