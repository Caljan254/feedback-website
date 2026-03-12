from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

try:
    with engine.connect() as conn:
        print("--- Users for VC Office (Dept ID: 1) ---")
        res = conn.execute(text('SELECT id, email, username, role, department_id, fullname FROM users WHERE department_id = 1'))
        for row in res.fetchall():
            print(row)
            
        print("\n--- VC Office Feedbacks (Dept ID: 1) ---")
        res = conn.execute(text('SELECT id, office, department_id, message FROM feedback WHERE department_id = 1'))
        for row in res.fetchall():
            print(row)
except Exception as e:
    print(f"Error: {e}")
