from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

with engine.connect() as conn:
    print("--- Users ---")
    res = conn.execute(text('SELECT id, email, username, role, department_id, fullname FROM users'))
    for row in res.fetchall():
        print(row)
