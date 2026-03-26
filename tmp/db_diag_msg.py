
import sqlalchemy
from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

with engine.connect() as connection:
    # Check last 5 entries with message
    result = connection.execute(text("SELECT id, rating, q_4, office, message, created_at FROM feedback ORDER BY id DESC LIMIT 5"))
    print("Last 5 Feedback Entries:")
    for row in result:
        print(f"ID: {row[0]}, Rating: '{row[1]}', Q_4: '{row[2]}', Office: {row[3]}, Message Length: {len(row[4]) if row[4] else 0}")
        if row[4]:
            print(f"  Message: {row[4][:100]}...")
