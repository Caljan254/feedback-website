
import pymysql
import os
from sqlalchemy import create_engine, text

# Get connection string from database.py if possible, or use the one I saw
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Aaamumo254%@localhost/feedback_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

with engine.connect() as connection:
    # Check columns in feedback table
    result = connection.execute(text("DESCRIBE feedback"))
    print("Table Schema for 'feedback':")
    for row in result:
        print(row)
    
    # Check last 5 entries
    result = connection.execute(text("SELECT id, rating, q_4, office, created_at FROM feedback ORDER BY id DESC LIMIT 5"))
    print("\nLast 5 Feedback Entries:")
    for row in result:
        print(row)
