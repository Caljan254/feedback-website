from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

with engine.connect() as conn:
    print("--- Question Responses with Question ID NULL ---")
    res = conn.execute(text('SELECT count(*) FROM question_responses WHERE question_id IS NULL'))
    print(res.fetchone())
    
    print("\n--- Any 500 Validation Errors in Log? ---")
