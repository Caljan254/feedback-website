import pymysql
import os
from sqlalchemy import create_engine, text

def fix_db_error():
    # Use the connection string from database.py/init_db.py
    # SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
    # Note: user provided Aaamumo254% in logs. Let's use the env or the string we found.
    # The log shows Aaamumo254% (escaped in my python call as %%, but the string usually has %)
    
    db_url = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("Expanding column lengths to prevent 'Data too long' errors...")
            
            # Change rating and q_0-q_4 to VARCHAR(255)
            # Some entries like "Highly Professional & Helpful" or "International student admission" might be longer than expected if the DB defines them as VARCHAR(10)
            
            conn.execute(text("ALTER TABLE feedback MODIFY COLUMN rating VARCHAR(255) NULL"))
            conn.execute(text("ALTER TABLE feedback MODIFY COLUMN q_0 VARCHAR(255) NULL"))
            conn.execute(text("ALTER TABLE feedback MODIFY COLUMN q_1 VARCHAR(255) NULL"))
            conn.execute(text("ALTER TABLE feedback MODIFY COLUMN q_2 VARCHAR(255) NULL"))
            conn.execute(text("ALTER TABLE feedback MODIFY COLUMN q_3 VARCHAR(255) NULL"))
            conn.execute(text("ALTER TABLE feedback MODIFY COLUMN q_4 VARCHAR(255) NULL"))
            
            conn.commit()
            print("✅ Database schema updated successfully. All columns now support 255 characters.")
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    fix_db_error()
