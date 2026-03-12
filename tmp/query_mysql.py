from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

with engine.connect() as conn:
    print("--- Departments ---")
    res = conn.execute(text('SELECT id, name FROM departments'))
    for row in res.fetchall():
        print(row)
    
    print("\n--- VC Office Feedback ---")
    res = conn.execute(text('SELECT id, office, department_id, message FROM feedback WHERE office LIKE "%vice%" OR office LIKE "%vc%" OR office LIKE "%Vice Chancellor%"'))
    for row in res.fetchall():
        print(row)
        
    print("\n--- All feedback office distribution ---")
    res = conn.execute(text('SELECT office, department_id, count(*) FROM feedback GROUP BY office, department_id'))
    for row in res.fetchall():
        print(row)
