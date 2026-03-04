
import sys
import os

# Add current directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Feedback

def check_promises():
    db = SessionLocal()
    try:
        feedback = db.query(Feedback).all()
        found = False
        for f in feedback:
            # Check rating column
            if f.rating == '[object Promise]':
                print(f"Found [object Promise] in feedback ID {f.id}, column rating")
                # Try to recover from q_4 or other columns if possible, else N/A
                f.rating = f.q_4 if (f.q_4 and f.q_4 != '[object Promise]') else 'N/A'
                found = True
            
            # Also check q_0 to q_4
            for i in range(5):
                col = f"q_{i}"
                val = getattr(f, col)
                if val == '[object Promise]':
                    print(f"Found [object Promise] in feedback ID {f.id}, column {col}")
                    setattr(f, col, 'N/A')
                    found = True
                    
        if found:
            db.commit()
            print("Fixed existing database entries.")
        else:
            print("No database entries with [object Promise] found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_promises()
